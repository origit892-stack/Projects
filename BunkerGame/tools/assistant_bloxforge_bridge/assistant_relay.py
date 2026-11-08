#!/usr/bin/env python3
"""
Assistant Local Relay - credential-free access to authenticated bridge
Binds ONLY 127.0.0.1, injects token locally, proxies only to 127.0.0.1:62412
Endpoints: POST /task, GET /status/<id>, GET /health
No shell, no filesystem browsing, bounded sizes/timeouts.
"""
import os
import sys
import json
import re
import time
import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, unquote

BRIDGE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BRIDGE_DIR, "token.txt")
PORT_FILE = os.path.join(BRIDGE_DIR, "port.txt")
RELAY_PORT_FILE = os.path.join(BRIDGE_DIR, "relay_port.txt")
RELAY_PID_FILE = os.path.join(BRIDGE_DIR, "assistant_relay.pid")
LOGS_DIR = os.path.join(BRIDGE_DIR, "logs")
RELAY_LOG = os.path.join(LOGS_DIR, "assistant_relay.log")

HOST = "127.0.0.1"
RELAY_DEFAULT_PORT = 62413
BRIDGE_HOST = "127.0.0.1"
# Bridge port is dynamic, read from port.txt
RELAY_PORT = RELAY_DEFAULT_PORT
BRIDGE_PORT = 62412  # will be read from file

REQ_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")

def get_bridge_port():
    try:
        with open(PORT_FILE, "r") as f:
            v = int(f.read().strip().split()[0])
            if 1024 <= v <= 65535:
                return v
    except Exception:
        pass
    return 62412

def get_relay_port():
    try:
        if os.path.exists(RELAY_PORT_FILE):
            with open(RELAY_PORT_FILE, "r") as f:
                v = int(f.read().strip().split()[0])
                if 1024 <= v <= 65535:
                    return v
    except Exception:
        pass
    return RELAY_DEFAULT_PORT

def get_token():
    try:
        with open(TOKEN_FILE, "r") as f:
            tok = f.read().strip()
            if tok:
                return tok
    except Exception as e:
        pass
    return None

def log(msg):
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    line = f"[{ts}] {msg}\n"
    # Only write to log file, and to stdout if TTY to avoid duplication when redirected
    try:
        with open(RELAY_LOG, "a") as lf:
            lf.write(line)
    except Exception:
        pass
    try:
        if sys.stdout.isatty():
            sys.stdout.write(line)
            sys.stdout.flush()
    except Exception:
        pass

class RelayHandler(BaseHTTPRequestHandler):
    def _send_json(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _proxy_to_bridge(self, method, path, body_bytes, content_type):
        # Read bridge port and token locally, inject auth
        bridge_port = get_bridge_port()
        token = get_token()
        if not token:
            self._send_json(500, {"error": "relay_misconfigured", "message": "bridge token unavailable"})
            return
        # Bounded timeouts
        timeout = 30 if method == "POST" else 10
        # Basic size check already done by caller; enforce again
        if body_bytes and len(body_bytes) > 64*1024:
            self._send_json(413, {"error": "payload_too_large"})
            return
        headers = {
            "Content-Type": content_type or "application/json",
            "Content-Length": str(len(body_bytes) if body_bytes else 0),
            "Accept": "application/json",
            "X-Bridge-Token": token,
            "Cache-Control": "no-store",
        }
        conn = http.client.HTTPConnection(BRIDGE_HOST, bridge_port, timeout=timeout)
        try:
            conn.request(method, path, body=body_bytes, headers=headers)
            resp = conn.getresponse()
            resp_body = resp.read()
            # Preserve status and content-type
            ctype = resp.getheader("Content-Type") or "application/json"
            self.send_response(resp.status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(resp_body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(resp_body)
            # Log without credential
            log(f"PROXY {method} {path} -> {resp.status} ({len(resp_body)} bytes)")
        except socket.timeout:
            self._send_json(504, {"error": "bridge_timeout", "message": "bridge did not respond in time"})
        except Exception as e:
            log(f"PROXY ERROR {method} {path}: {e}")
            self._send_json(502, {"error": "bridge_unavailable", "message": str(e)[:500]})
        finally:
            try:
                conn.close()
            except:
                pass

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/task":
            self._send_json(404, {"error": "not_found", "path": parsed.path})
            return
        # Bounded size
        length = int(self.headers.get("Content-Length") or 0)
        if length > 64*1024:
            self._send_json(413, {"error": "payload_too_large"})
            return
        ctype = self.headers.get("Content-Type") or ""
        if "application/json" not in ctype:
            self._send_json(415, {"error": "unsupported_media_type"})
            return
        body = self.rfile.read(length) if length else b""
        # Basic JSON validation without logging secret
        try:
            data = json.loads(body.decode("utf-8") if body else "{}")
            # Quick validation without exposing token
            if not isinstance(data.get("request_id"), str) or not REQ_ID_RE.match(data.get("request_id") or ""):
                # Still proxy to let bridge return proper error (preserve contract)
                pass
        except Exception:
            # Let bridge handle invalid json
            pass
        log(f"RELAY POST /task from {self.client_address[0]} ({len(body)} bytes, no credential)")
        self._proxy_to_bridge("POST", "/task", body, "application/json")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/health":
            # Relay health - does not require credential, does not expose token
            bridge_port = get_bridge_port()
            # Optionally check bridge health internally without exposing token in response
            # For now, just report relay health
            self._send_json(200, {"ok": True, "service": "assistant_relay", "relay_host": HOST, "relay_port": RELAY_PORT, "bridge_host": BRIDGE_HOST, "bridge_port": bridge_port, "uptime": "ok"})
            log(f"GET /health from {self.client_address[0]} -> 200")
            return
        if path.startswith("/status/"):
            # Validate request_id
            raw_id = unquote(path[len("/status/"):])
            request_id = raw_id.strip("/")
            # Strip query string if any (already removed by urlparse, but be safe)
            if "?" in request_id:
                request_id = request_id.split("?")[0]
            if not REQ_ID_RE.match(request_id):
                self._send_json(400, {"error": "invalid_request_id"})
                return
            log(f"RELAY GET /status/{request_id} from {self.client_address[0]}")
            self._proxy_to_bridge("GET", f"/status/{request_id}", b"", "application/json")
            return
        self._send_json(404, {"error": "not_found", "path": path})

    def log_message(self, format, *args):
        log("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format%args))

def main():
    global RELAY_PORT
    desired = get_relay_port()
    # Ensure logs dir
    os.makedirs(LOGS_DIR, exist_ok=True)
    httpd = None
    actual_port = None
    try:
        server_address = (HOST, desired)
        httpd = HTTPServer(server_address, RelayHandler)
        actual_port = desired
        log(f"Relay bound to desired port {desired}")
    except OSError as e:
        if e.errno == 48:
            log(f"Port {desired} in use, trying free port")
            httpd = HTTPServer((HOST, 0), RelayHandler)
            actual_port = httpd.socket.getsockname()[1]
            log(f"Relay autonomous port {actual_port}")
        else:
            raise
    bound = httpd.socket.getsockname()
    if bound[0] != "127.0.0.1":
        log(f"ERROR: relay bound to non-loopback {bound}")
        httpd.server_close()
        raise RuntimeError(f"Bound to non-loopback {bound}")
    RELAY_PORT = actual_port
    # Write actual port file atomically
    tmp = RELAY_PORT_FILE + ".tmp"
    with open(tmp, "w") as f:
        f.write(str(actual_port))
    os.rename(tmp, RELAY_PORT_FILE)
    log(f"Assistant Relay starting HOST={HOST} PORT={RELAY_PORT} -> bridge {BRIDGE_HOST}:{get_bridge_port()} BRIDGE_DIR={BRIDGE_DIR}")
    with open(RELAY_PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        log("Relay shutting down")
        httpd.server_close()

if __name__ == "__main__":
    import socket
    main()
