#!/usr/bin/env python3
"""Local bridge daemon for Chat Bridge v2 (multi-provider). Listens on 127.0.0.1 only."""
import argparse
import json
import os
import sys
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import db

VERSION = db.VERSION
STARTED_AT = time.time()

def utc_now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

DEFAULT_CONFIG = Path.home() / ".chat-bridge" / "config.json"
DEFAULT_DB = Path.home() / ".chat-bridge" / "chat-bridge.sqlite3"

def load_token(config_path):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return str(json.load(f).get("token") or "").strip()
    except Exception:
        return ""

def create_token():
    return uuid.uuid4().hex + uuid.uuid4().hex

def save_token(config_path, token):
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if config_path.exists():
        try:
            existing = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            existing = {}
    existing["token"] = token
    config_path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    os.chmod(config_path, 0o600)

class Api:
    def __init__(self, db_path, token, config_path):
        self.db_path = str(db_path)
        self.token = token
        self.config_path = str(config_path)
        self.started_at = utc_now()
        self.diags = {}  # provider -> latest diagnostic payload from the extension

    def authed(self, raw):
        if not self.token:
            return False
        return raw == f"Bearer {self.token}"

    def authed_from(self, headers):
        """Accept both the v2 Authorization header and the v1 X-Chat-Bridge-Token header."""
        return (self.authed(headers.get("authorization", ""))
                or headers.get("x-chat-bridge-token", "") == self.token)

    def healthz(self):
        return {"ok": True, "version": VERSION, "storage": self.db_path,
                "uptime_s": int(time.time() - STARTED_AT), "providers": db.provider_stats(self.db_path)}

    def providers(self):
        stats = db.provider_stats(self.db_path)
        out = {}
        for provider, info in stats.items():
            diag = self.diags.get(provider)
            out[provider] = {**info, "capture_failed": bool(diag and diag.get("capture_failed")),
                             "diag": diag}
        return out

    def handle(self, method, path, headers, body):
        if path == "/healthz":
            return 200, self.healthz()
        if not self.authed_from(headers):
            return 401, {"ok": False, "error": "invalid token"}
        try:
            if method == "GET" and path == "/health":
                return 200, self.healthz()
            if method == "GET" and path == "/providers":
                return 200, {"ok": True, "providers": self.providers()}
            if method == "POST" and path == "/diag":
                payload = json.loads(body.decode("utf-8"))
                provider = db.normalize_provider(payload.get("provider"))
                self.diags[provider] = {"ts": utc_now(), **payload}
                return 200, {"ok": True}
            if method == "POST" and path == "/capture":
                payload = json.loads(body.decode("utf-8"))
                result = db.save_snapshot(self.db_path, payload)
                return 200, {"ok": True, **result}
            if method == "POST" and path == "/next-action":
                payload = json.loads(body.decode("utf-8"))
                provider = db.normalize_provider(payload.get("provider") or "chatgpt")
                conversation_id = str(payload.get("conversation_id") or "")
                allow = bool(payload.get("allow_agent_send"))
                action = db.claim_action(self.db_path, conversation_id, allow, provider=provider)
                if not action:
                    return 200, {"status": "idle", "action": None}
                # The `action` object keeps the v1 extension working against the v2 daemon;
                # v2's service worker consumes the same shape.
                return 200, {"status": "send", "action": {"id": action["id"],
                                                          "provider": provider,
                                                          "conversation_id": action["conversation_id"],
                                                          "message": action["message"],
                                                          "timeout_ms": 90000}}
            if method == "POST" and path == "/action-result":
                payload = json.loads(body.decode("utf-8"))
                action_id = str(payload.get("action_id") or "")
                changed = db.complete_action(self.db_path, action_id,
                                             str(payload.get("status") or "failed"),
                                             str(payload.get("response") or ""),
                                             str(payload.get("error") or ""))
                return 200, {"ok": changed}
            if method == "GET" and path.startswith("/actions/"):
                row = db.get_action(self.db_path, path.rsplit("/", 1)[-1])
                if not row:
                    return 404, {"ok": False, "error": "not found"}
                return 200, {"ok": True, "action": row}
            if method == "POST" and path == "/rotate-token":
                new_token = create_token()
                save_token(self.config_path, new_token)
                self.token = new_token
                return 200, {"ok": True, "token": new_token}
        except ValueError as e:
            return 400, {"ok": False, "error": str(e)}
        return 404, {"ok": False, "error": "unknown endpoint"}

def run(port, db_path, config_path, verbose=True):
    config_path = Path(config_path)
    token = load_token(config_path)
    if not token:
        token = create_token()
        save_token(config_path, token)
        print(f"Created local token at {config_path}", flush=True)
    api = Api(db_path, token, config_path)
    db.init_db(db_path)
    print(f"Chat Bridge daemon v{VERSION} listening on 127.0.0.1:{port}", flush=True)

    class Handler(BaseHTTPRequestHandler):
        server_version = f"ChatBridge/{VERSION}"

        def _respond(self, code, payload):
            data = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Access-Control-Allow-Origin", f"http://127.0.0.1:{port}")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.end_headers()
            self.wfile.write(data)

        def do_OPTIONS(self):
            self._respond(204, {})

        def do_GET(self):
            code, payload = api.handle("GET", urlsplit(self.path).path, self.headers, b"")
            self._respond(code, payload)

        def do_POST(self):
            length = min(int(self.headers.get("Content-Length") or 0), 30 * 1024 * 1024)
            body = self.rfile.read(length)
            code, payload = api.handle("POST", urlsplit(self.path).path, self.headers, body)
            if verbose and code == 200:
                print(f"{self.path} -> {json.dumps(payload)[:220]}", flush=True)
            self._respond(code, payload)

        def log_message(self, format, *args):
            pass

    server = HTTPServer(("127.0.0.1", port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

def main():
    parser = argparse.ArgumentParser(description="Chat Bridge local daemon (v2)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("CHAT_BRIDGE_PORT", "8765")))
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    args = parser.parse_args()
    run(args.port, args.db, args.config)

if __name__ == "__main__":
    main()
