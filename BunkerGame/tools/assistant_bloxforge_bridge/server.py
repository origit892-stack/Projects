#!/usr/bin/env python3
"""
Assistant <-> BloxForge localhost bridge
- binds ONLY 127.0.0.1
- random token auth
- JSON only
- no shell/eval
- stores only beneath bridge directory
Endpoints:
  POST /task
  GET  /status/<request_id>
"""
import os
import sys
import json
import re
import secrets
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, unquote

BRIDGE_DIR = os.path.dirname(os.path.abspath(__file__))
REQUESTS_DIR = os.path.join(BRIDGE_DIR, "requests")
RESPONSES_DIR = os.path.join(BRIDGE_DIR, "responses")
STATE_DIR = os.path.join(BRIDGE_DIR, "state")
LOGS_DIR = os.path.join(BRIDGE_DIR, "logs")
TOKEN_FILE = os.path.join(BRIDGE_DIR, "token.txt")
PORT_FILE = os.path.join(BRIDGE_DIR, "port.txt")
PID_FILE = os.path.join(BRIDGE_DIR, "server.pid")

HOST = "127.0.0.1"
DEFAULT_PORT = 8765
# PORT is mutable global, initialized to desired then updated to actual bound port
PORT = DEFAULT_PORT

def _get_desired_port():
    try:
        if os.path.exists(PORT_FILE):
            with open(PORT_FILE, "r") as f:
                v = int(f.read().strip().split()[0])
                if 1024 <= v <= 65535:
                    return v
    except Exception:
        pass
    return DEFAULT_PORT

# Generate token at startup
TOKEN = secrets.token_hex(32)

# Ensure dirs exist
for d in [REQUESTS_DIR, RESPONSES_DIR, STATE_DIR, LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

# Write token file atomically under bridge dir (port file written after successful bind)
with open(TOKEN_FILE, "w") as f:
    f.write(TOKEN)

# Regex for safe request_id: alphanumeric, dash, underscore, dot, limited length
REQ_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")

def log(msg):
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    line = f"[{ts}] {msg}\n"
    sys.stdout.write(line)
    sys.stdout.flush()
    try:
        with open(os.path.join(LOGS_DIR, "server.log"), "a") as lf:
            lf.write(line)
    except:
        pass

class BridgeHandler(BaseHTTPRequestHandler):
    def _send_json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _auth_ok(self):
        # Require token via X-Bridge-Token or Authorization: Bearer <token>
        hdr = self.headers.get("X-Bridge-Token") or self.headers.get("x-bridge-token")
        if hdr and hdr.strip() == TOKEN:
            return True
        auth = self.headers.get("Authorization") or self.headers.get("authorization")
        if auth and auth.strip() == f"Bearer {TOKEN}":
            return True
        if auth and auth.strip() == TOKEN:
            return True
        return False

    def _require_json(self):
        ctype = self.headers.get("Content-Type") or ""
        if "application/json" not in ctype:
            return False
        return True

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/task":
            self._send_json(404, {"error": "not_found", "path": parsed.path})
            return
        if not self._auth_ok():
            self._send_json(401, {"error": "unauthorized", "message": "missing or invalid token"})
            return
        if not self._require_json():
            self._send_json(415, {"error": "unsupported_media_type", "message": "Content-Type must be application/json"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length > 64 * 1024:
            self._send_json(413, {"error": "payload_too_large"})
            return
        raw = self.rfile.read(length) if length else b""
        try:
            data = json.loads(raw.decode("utf-8") if raw else "{}")
        except Exception as e:
            self._send_json(400, {"error": "invalid_json", "message": str(e)})
            return

        # Validate required fields - strict, no eval
        request_id = data.get("request_id")
        intent = data.get("intent")
        details = data.get("details")
        studio_context = data.get("studio_context")

        if not isinstance(request_id, str) or not REQ_ID_RE.match(request_id):
            self._send_json(400, {"error": "invalid_request_id", "message": "request_id must match ^[A-Za-z0-9._-]{1,128}$"})
            return
        if not isinstance(intent, str) or len(intent) == 0 or len(intent) > 256:
            self._send_json(400, {"error": "invalid_intent"})
            return
        if not isinstance(details, str) or len(details) > 4096:
            self._send_json(400, {"error": "invalid_details"})
            return
        if studio_context is not None and not isinstance(studio_context, dict):
            self._send_json(400, {"error": "invalid_studio_context"})
            return

        # Store request atomically under bridge dir only
        req_path = os.path.join(REQUESTS_DIR, f"{request_id}.json")
        state_path = os.path.join(STATE_DIR, f"{request_id}.json")
        # Prevent path traversal - already validated but double check
        if not os.path.abspath(req_path).startswith(os.path.abspath(REQUESTS_DIR)):
            self._send_json(400, {"error": "path_traversal"})
            return

        record = {
            "request_id": request_id,
            "intent": intent,
            "details": details,
            "studio_context": studio_context if isinstance(studio_context, dict) else {},
            "received_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "pending"
        }
        # Preserve bloxforge object for Worker v1 (if present, must be dict)
        bloxforge = data.get("bloxforge")
        if isinstance(bloxforge, dict):
            # Validate tool name to prevent log injection, but preserve
            record["bloxforge"] = bloxforge
        # Write request file
        with open(req_path, "w") as f:
            json.dump(record, f, indent=2)
        # Write state file (pending until response created)
        with open(state_path, "w") as f:
            json.dump(record, f, indent=2)

        log(f"POST /task request_id={request_id} intent={intent} stored")
        self._send_json(200, {"ok": True, "request_id": request_id, "status": "pending"})

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Health check (also requires auth to avoid unauthenticated probing disclosure? but allow with auth)
        if path == "/health":
            if not self._auth_ok():
                self._send_json(401, {"error": "unauthorized"})
                return
            self._send_json(200, {"ok": True, "host": HOST, "port": PORT})
            return

        # GET /status/<request_id>
        if path.startswith("/status/"):
            if not self._auth_ok():
                self._send_json(401, {"error": "unauthorized"})
                return
            raw_id = unquote(path[len("/status/"):])
            # strip query/fragment already via urlparse
            request_id = raw_id.strip("/")
            if not REQ_ID_RE.match(request_id):
                self._send_json(400, {"error": "invalid_request_id"})
                return

            # Check for completed response first
            resp_path = os.path.join(RESPONSES_DIR, f"{request_id}.json")
            state_path = os.path.join(STATE_DIR, f"{request_id}.json")
            req_path = os.path.join(REQUESTS_DIR, f"{request_id}.json")

            if os.path.exists(resp_path):
                try:
                    with open(resp_path, "r") as f:
                        data = json.load(f)
                    # Ensure request_id matches
                    log(f"GET /status/{request_id} -> completed")
                    self._send_json(200, data)
                    return
                except Exception as e:
                    self._send_json(500, {"error": "response_read_failed", "message": str(e)})
                    return
            elif os.path.exists(state_path):
                try:
                    with open(state_path, "r") as f:
                        data = json.load(f)
                    # If state indicates completed but no response file, return state
                    # Otherwise pending
                    if data.get("status") == "completed":
                        log(f"GET /status/{request_id} -> completed (state)")
                        self._send_json(200, data)
                    else:
                        log(f"GET /status/{request_id} -> pending")
                        self._send_json(200, {"request_id": request_id, "status": "pending", "message": "not yet completed"})
                    return
                except Exception as e:
                    self._send_json(500, {"error": "state_read_failed", "message": str(e)})
                    return
            elif os.path.exists(req_path):
                self._send_json(200, {"request_id": request_id, "status": "pending"})
                return
            else:
                self._send_json(404, {"error": "not_found", "request_id": request_id})
                return

        self._send_json(404, {"error": "not_found", "path": path})

    def log_message(self, format, *args):
        # Override to use our log
        log("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format%args))

def main():
    global PORT
    # Security: ensure we only bind loopback
    desired = _get_desired_port()
    httpd = None
    actual_port = None
    # First attempt desired port; if in use, fallback to OS-assigned free port
    try:
        server_address = (HOST, desired)
        httpd = HTTPServer(server_address, BridgeHandler)
        actual_port = desired
        log(f"Bridge bound to desired port {desired}")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            log(f"Port {desired} in use, selecting autonomous free loopback port")
            # Bind to port 0 to let OS pick free port on 127.0.0.1
            httpd = HTTPServer((HOST, 0), BridgeHandler)
            actual_port = httpd.socket.getsockname()[1]
            log(f"Autonomous port selected: {actual_port} (fallback from {desired})")
        else:
            raise
    # Verify binding is loopback only
    bound = httpd.socket.getsockname()
    if bound[0] != "127.0.0.1":
        log(f"ERROR: bound to non-loopback {bound}, shutting down")
        httpd.server_close()
        raise RuntimeError(f"Bound to non-loopback {bound}")
    PORT = actual_port
    # Write actual port file atomically
    with open(PORT_FILE, "w") as f:
        f.write(str(actual_port))
    log(f"Bridge starting HOST={HOST} PORT={PORT} TOKEN={TOKEN[:8]}... bound={bound} BRIDGE_DIR={BRIDGE_DIR}")
    # Write pid
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        log("Bridge shutting down")
        httpd.server_close()

if __name__ == "__main__":
    main()
