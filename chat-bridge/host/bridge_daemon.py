#!/usr/bin/env python3
"""Local loopback HTTP bridge between the Chrome extension and SQLite."""
from __future__ import annotations

import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from db import claim_action, complete_action, conversation_count, init_db, save_snapshot

CONFIG_PATH = Path(os.environ.get("CHAT_BRIDGE_CONFIG", "~/.chat-bridge/config.json")).expanduser()


def load_config():
    if not CONFIG_PATH.exists():
        raise SystemExit(f"Missing {CONFIG_PATH}. Run install_mac.sh first.")
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    if not cfg.get("token") or len(cfg["token"]) < 32:
        raise SystemExit("Invalid local token in config.json")
    cfg["db_path"] = str(Path(cfg.get("db_path", "~/.chat-bridge/chat-bridge.sqlite3")).expanduser())
    return cfg


CONFIG = load_config()
DB_PATH = CONFIG["db_path"]
TOKEN = CONFIG["token"]
init_db(DB_PATH)


class Handler(BaseHTTPRequestHandler):
    server_version = "ChatBridge/0.1"

    def log_message(self, fmt, *args):
        # Do not log message bodies, tokens or conversation content.
        print(f"[chat-bridge] {self.address_string()} {fmt % args}")

    def _origin_headers(self):
        origin = self.headers.get("Origin", "")
        if origin.startswith("chrome-extension://"):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Chat-Bridge-Token")
            self.send_header("Access-Control-Max-Age", "600")

    def _send(self, code: int, payload: dict):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self._origin_headers()
        self.end_headers()
        self.wfile.write(data)

    def _authorized(self) -> bool:
        origin = self.headers.get("Origin", "")
        # Browser requests must originate from the extension, not an arbitrary web page.
        if origin and not origin.startswith("chrome-extension://"):
            return False
        supplied = self.headers.get("X-Chat-Bridge-Token", "")
        return hmac.compare_digest(supplied, TOKEN)

    def do_OPTIONS(self):
        origin = self.headers.get("Origin", "")
        if not origin.startswith("chrome-extension://"):
            self._send(403, {"error": "Origin not allowed"})
            return
        self.send_response(204)
        self._origin_headers()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        if urlparse(self.path).path != "/health":
            self._send(404, {"error": "Not found"})
            return
        if not self._authorized():
            self._send(401, {"error": "Unauthorized"})
            return
        self._send(200, {"ok": True, "conversation_count": conversation_count(DB_PATH), "storage": "local SQLite"})

    def do_POST(self):
        if not self._authorized():
            self._send(401, {"error": "Unauthorized"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > 2_000_000:
                self._send(413, {"error": "Request body must be between 1 byte and 2 MB"})
                return
            payload = json.loads(self.rfile.read(size).decode("utf-8"))
            path = urlparse(self.path).path
            if path == "/capture":
                self._send(200, {"ok": True, **save_snapshot(DB_PATH, payload)})
            elif path == "/next-action":
                action = claim_action(DB_PATH, str(payload.get("conversation_id", "")), bool(payload.get("allow_agent_send")))
                if action:
                    action["timeout_ms"] = 90000
                self._send(200, {"action": action})
            elif path == "/action-result":
                changed = complete_action(DB_PATH, str(payload.get("action_id", "")),
                    str(payload.get("status", "")), str(payload.get("response", "")), str(payload.get("error", "")))
                self._send(200, {"ok": changed})
            else:
                self._send(404, {"error": "Not found"})
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self._send(400, {"error": str(exc)[:500]})
        except Exception as exc:
            self._send(500, {"error": f"Internal error: {type(exc).__name__}"})


def main():
    host = "127.0.0.1"
    port = int(os.environ.get("CHAT_BRIDGE_PORT", "8765"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Chat Bridge local service listening on http://{host}:{port}")
    print(f"SQLite archive: {DB_PATH}")
    print("Keep this terminal window open while using Chat Bridge. Press Ctrl+C to stop.")
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        print("\nStopping Chat Bridge.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
