#!/usr/bin/env python3
"""
BloxForge Worker v1 - connects assistant_bloxforge_bridge queue to BloxForge MCP :58741/mcp
Deterministic transport/orchestration, NOT an AI agent.
Read-only allowlist enforced.
"""
import os
import sys
import json
import re
import time
import hashlib
import traceback
from pathlib import Path
import http.client
import socket

BRIDGE_DIR = os.path.dirname(os.path.abspath(__file__))
REQUESTS_DIR = os.path.join(BRIDGE_DIR, "requests")
STATE_DIR = os.path.join(BRIDGE_DIR, "state")
RESPONSES_DIR = os.path.join(BRIDGE_DIR, "responses")
LOGS_DIR = os.path.join(BRIDGE_DIR, "logs")
WORKER_LOG = os.path.join(LOGS_DIR, "worker.log")
WORKER_PID_FILE = os.path.join(BRIDGE_DIR, "worker.pid")

BLOXFORGE_MCP_URL = "http://127.0.0.1:58741/mcp"
BLOXFORGE_HOST = "127.0.0.1"
BLOXFORGE_PORT = 58741
BLOXFORGE_PATH = "/mcp"

ALLOWLIST = {
    "get_connected_instances",
    "get_scene_summary",
    "get_session_summary",
    "get_transport_diagnostics",
    "tool_catalog_search",
}

REQ_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")

def log(msg):
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    line = f"[{ts}] {msg}\n"
    # Write to stdout (which is redirected to log file via nohup) and also ensure flush
    # Avoid double-write: only write to stdout, rely on redirection; also try file write only if stdout is not already the log file
    # For robustness, write only once to log file directly, not to stdout when started via nohup
    # To avoid duplication, write only to file when running as daemon
    try:
        with open(WORKER_LOG, "a") as lf:
            lf.write(line)
    except Exception:
        pass
    # Also mirror to stdout only if not already redirected to log file (avoid duplicate)
    try:
        # Check if stdout is a TTY (interactive) - if so, also echo
        if sys.stdout.isatty():
            sys.stdout.write(line)
            sys.stdout.flush()
    except Exception:
        pass

def atomic_write(path, data):
    tmp = path + ".tmp." + str(os.getpid())
    try:
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.rename(tmp, path)
    finally:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except:
            pass

def is_temp_file(name):
    # Do not process temporary files (e.g., .tmp, ~, .swp)
    if name.startswith("."):
        return True
    if name.endswith(".tmp") or name.endswith(".tmp."+str(os.getpid())) or ".tmp." in name:
        return True
    if name.endswith("~"):
        return True
    return False

def parse_sse_body(body_text):
    """
    Parse BloxForge SSE-style response:
    event: message
    data: {...JSON...}
    Do NOT assume plain JSON.
    """
    body_text = body_text.strip()
    if not body_text:
        raise ValueError("Empty response body")
    # Try plain JSON first
    if body_text.startswith("{"):
        try:
            return json.loads(body_text)
        except:
            pass
    # Parse SSE
    data_lines = []
    for line in body_text.splitlines():
        line=line.strip()
        if line.startswith("data:"):
            data = line[len("data:"):].strip()
            data_lines.append(data)
        elif line.startswith("{") and line.endswith("}"):
            # Fallback: line is JSON without event prefix
            data_lines.append(line)
    if not data_lines:
        # No data lines found, try to find JSON object in body
        # Find first { and last }
        start = body_text.find("{")
        end = body_text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = body_text[start:end+1]
            try:
                return json.loads(candidate)
            except Exception as e:
                raise ValueError(f"No SSE data line and plain JSON parse failed: {e}, body: {body_text[:500]}")
        raise ValueError(f"No SSE data found in body: {body_text[:500]}")
    # Join data lines (usually one)
    # If multiple data events, take last or combine? Take last complete JSON
    last = data_lines[-1]
    try:
        return json.loads(last)
    except Exception as e:
        # If data is multiple JSON objects concatenated, try to parse combined
        combined = "\n".join(data_lines)
        try:
            return json.loads(combined)
        except:
            raise ValueError(f"Failed to parse SSE data as JSON: {e}, data: {last[:500]}")

def send_mcp_tool_call(tool, arguments, timeout=30):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool,
            "arguments": arguments or {}
        }
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Content-Length": str(len(body)),
    }
    conn = http.client.HTTPConnection(BLOXFORGE_HOST, BLOXFORGE_PORT, timeout=timeout)
    try:
        conn.request("POST", BLOXFORGE_PATH, body=body, headers=headers)
        resp = conn.getresponse()
        status = resp.status
        resp_body = resp.read().decode("utf-8", errors="replace")
        if status != 200:
            raise RuntimeError(f"BloxForge MCP HTTP {status}: {resp_body[:1000]}")
        # Parse SSE or JSON
        parsed = parse_sse_body(resp_body)
        return parsed
    finally:
        try:
            conn.close()
        except:
            pass

def process_request(req_path):
    req_file = os.path.basename(req_path)
    request_id = req_file[:-5] if req_file.endswith(".json") else req_file
    # Validate request_id format
    if not REQ_ID_RE.match(request_id):
        log(f"SKIP invalid request_id format: {request_id}")
        return False
    # Check for temp file
    if is_temp_file(req_file):
        return False
    # Atomic claiming: try to create claim file exclusively
    claim_path = os.path.join(STATE_DIR, f"{request_id}.claim")
    state_path = os.path.join(STATE_DIR, f"{request_id}.json")
    resp_path = os.path.join(RESPONSES_DIR, f"{request_id}.json")
    # If already completed (response exists), skip
    if os.path.exists(resp_path):
        return False
    # If state says completed, skip
    if os.path.exists(state_path):
        try:
            with open(state_path, "r") as f:
                st = json.load(f)
                if st.get("status") in ("completed", "failed", "processing"):
                    # If processing, check age - if stale >5min, allow? For V1, treat as claimed, skip
                    if st.get("status") == "processing":
                        # Check if claimed too long ago (stale worker)
                        # For now, skip to avoid duplicate
                        return False
                    if st.get("status") in ("completed", "failed"):
                        return False
        except Exception:
            pass
    # Try atomic claim
    try:
        fd = os.open(claim_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
    except FileExistsError:
        return False
    except Exception as e:
        log(f"Claim failed for {request_id}: {e}")
        return False

    # We have claimed it, now process
    try:
        # Read request file
        try:
            with open(req_path, "r") as f:
                req_data = json.load(f)
        except Exception as e:
            err_msg = f"Malformed JSON in request: {e}"
            log(f"FAIL {request_id}: {err_msg}")
            fail_resp = {
                "request_id": request_id,
                "status": "failed",
                "source": "bloxforge_worker",
                "error": {"code": "MALFORMED_REQUEST_JSON", "message": err_msg},
                "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            atomic_write(resp_path, fail_resp)
            fail_state = {
                "request_id": request_id,
                "status": "failed",
                "source": "bloxforge_worker",
                "error": {"code": "MALFORMED_REQUEST_JSON", "message": err_msg},
                "completed_at": fail_resp["completed_at"]
            }
            atomic_write(state_path, fail_state)
            try: os.remove(claim_path)
            except: pass
            return True

        # Validate intent
        intent = req_data.get("intent")
        if intent != "bloxforge_tool_call":
            err_msg = f"Intent must be bloxforge_tool_call, got {intent}"
            log(f"FAIL {request_id}: {err_msg}")
            fail_resp = {
                "request_id": request_id,
                "status": "failed",
                "source": "bloxforge_worker",
                "error": {"code": "INVALID_INTENT", "message": err_msg},
                "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            atomic_write(resp_path, fail_resp)
            atomic_write(state_path, {**fail_resp, "intent": intent})
            try: os.remove(claim_path)
            except: pass
            return True

        blox = req_data.get("bloxforge")
        if not isinstance(blox, dict):
            err_msg = "Missing bloxforge object"
            log(f"FAIL {request_id}: {err_msg}")
            fail_resp = {
                "request_id": request_id,
                "status": "failed",
                "source": "bloxforge_worker",
                "error": {"code": "MISSING_BLOXFORGE_OBJECT", "message": err_msg},
                "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            atomic_write(resp_path, fail_resp)
            atomic_write(state_path, fail_resp)
            try: os.remove(claim_path)
            except: pass
            return True

        tool = blox.get("tool")
        if not isinstance(tool, str) or not tool:
            err_msg = "Missing bloxforge.tool"
            log(f"FAIL {request_id}: {err_msg}")
            fail_resp = {
                "request_id": request_id,
                "status": "failed",
                "source": "bloxforge_worker",
                "error": {"code": "MISSING_BLOXFORGE_TOOL", "message": err_msg},
                "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            atomic_write(resp_path, fail_resp)
            atomic_write(state_path, fail_resp)
            try: os.remove(claim_path)
            except: pass
            return True

        arguments = blox.get("arguments")
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            err_msg = "bloxforge.arguments must be object"
            log(f"FAIL {request_id}: {err_msg}")
            fail_resp = {
                "request_id": request_id,
                "status": "failed",
                "source": "bloxforge_worker",
                "error": {"code": "INVALID_ARGUMENTS", "message": err_msg},
                "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            atomic_write(resp_path, fail_resp)
            atomic_write(state_path, fail_resp)
            try: os.remove(claim_path)
            except: pass
            return True

        # Enforce read-only allowlist
        if tool not in ALLOWLIST:
            err_msg = f"Tool {tool} not allowed in V1 read-only allowlist"
            log(f"FAIL {request_id}: {err_msg} (no MCP call)")
            fail_resp = {
                "request_id": request_id,
                "status": "failed",
                "source": "bloxforge_worker",
                "error": {"code": "BLOXFORGE_TOOL_NOT_ALLOWED_V1", "message": err_msg, "allowlist": sorted(list(ALLOWLIST))},
                "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            atomic_write(resp_path, fail_resp)
            # Update state to failed
            fail_state = {
                "request_id": request_id,
                "intent": intent,
                "bloxforge_tool": tool,
                "status": "failed",
                "source": "bloxforge_worker",
                "error": fail_resp["error"],
                "completed_at": fail_resp["completed_at"]
            }
            atomic_write(state_path, fail_state)
            try: os.remove(claim_path)
            except: pass
            return True

        # Mark state as processing
        processing_state = {
            "request_id": request_id,
            "intent": intent,
            "bloxforge_tool": tool,
            "status": "processing",
            "source": "bloxforge_worker",
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "bloxforge_mcp": BLOXFORGE_MCP_URL
        }
        atomic_write(state_path, processing_state)
        log(f"PROCESSING {request_id} tool={tool} args={json.dumps(arguments)[:500]}")

        # Send to BloxForge MCP
        try:
            mcp_result = send_mcp_tool_call(tool, arguments, timeout=30)
            # BloxForge result is JSON-RPC result; extract result field if present
            # The parsed SSE body is the JSON-RPC envelope: {"jsonrpc":"2.0","id":1,"result":{...}} or {"error":...}
            actual_result = None
            if isinstance(mcp_result, dict):
                if "result" in mcp_result:
                    actual_result = mcp_result["result"]
                elif "error" in mcp_result:
                    # MCP returned error
                    raise RuntimeError(f"BloxForge MCP error: {mcp_result['error']}")
                else:
                    actual_result = mcp_result
            else:
                actual_result = mcp_result

            success_resp = {
                "request_id": request_id,
                "status": "completed",
                "source": "bloxforge",
                "bloxforge_tool": tool,
                "bloxforge_mcp": BLOXFORGE_MCP_URL,
                "result": actual_result,
                "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            atomic_write(resp_path, success_resp)
            completed_state = {
                "request_id": request_id,
                "intent": intent,
                "bloxforge_tool": tool,
                "status": "completed",
                "source": "bloxforge",
                "bloxforge_mcp": BLOXFORGE_MCP_URL,
                "completed_at": success_resp["completed_at"]
            }
            atomic_write(state_path, completed_state)
            log(f"COMPLETED {request_id} tool={tool}")
        except Exception as e:
            tb = traceback.format_exc()
            err_msg = str(e)[:2000]
            log(f"FAILED {request_id} tool={tool} error={err_msg}")
            # Distinguish BloxForge unavailable vs other
            code = "BLOXFORGE_MCP_ERROR"
            if "Connection" in err_msg or "timed out" in err_msg.lower() or "refused" in err_msg.lower():
                code = "BLOXFORGE_UNAVAILABLE"
            fail_resp = {
                "request_id": request_id,
                "status": "failed",
                "source": "bloxforge_worker",
                "error": {"code": code, "message": err_msg},
                "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "bloxforge_tool": tool,
                "bloxforge_mcp": BLOXFORGE_MCP_URL
            }
            atomic_write(resp_path, fail_resp)
            fail_state = {
                "request_id": request_id,
                "intent": intent,
                "bloxforge_tool": tool,
                "status": "failed",
                "source": "bloxforge_worker",
                "error": fail_resp["error"],
                "completed_at": fail_resp["completed_at"],
                "bloxforge_mcp": BLOXFORGE_MCP_URL
            }
            atomic_write(state_path, fail_state)

        try: os.remove(claim_path)
        except: pass
        return True
    except Exception as e:
        log(f"UNHANDLED ERROR for {request_id}: {e}\n{traceback.format_exc()}")
        try: os.remove(claim_path)
        except: pass
        return False

def main():
    log("BloxForge Worker v1 starting")
    log(f"Watching {REQUESTS_DIR}")
    log(f"BloxForge MCP {BLOXFORGE_MCP_URL}")
    log(f"Allowlist: {sorted(ALLOWLIST)}")
    # Ensure dirs
    for d in [REQUESTS_DIR, STATE_DIR, RESPONSES_DIR, LOGS_DIR]:
        os.makedirs(d, exist_ok=True)
    # Main loop
    while True:
        try:
            # List requests
            try:
                files = os.listdir(REQUESTS_DIR)
            except FileNotFoundError:
                time.sleep(1)
                continue
            # Filter json files, skip temp
            json_files = [f for f in files if f.endswith(".json") and not is_temp_file(f)]
            # Sort by mtime for FIFO
            json_files.sort(key=lambda f: os.path.getmtime(os.path.join(REQUESTS_DIR, f)) if os.path.exists(os.path.join(REQUESTS_DIR, f)) else 0)
            processed = 0
            for fname in json_files:
                req_path = os.path.join(REQUESTS_DIR, fname)
                # Skip temp files already
                if not os.path.isfile(req_path):
                    continue
                # Process one at a time to ensure atomic
                did = process_request(req_path)
                if did:
                    processed += 1
                    # Brief pause to avoid hammering MCP
                    time.sleep(0.1)
            if processed == 0:
                time.sleep(0.5)
            else:
                # If we processed, loop quickly to catch next
                time.sleep(0.1)
        except KeyboardInterrupt:
            log("Worker interrupted, exiting")
            break
        except Exception as e:
            log(f"Worker loop error: {e}\n{traceback.format_exc()}")
            time.sleep(1)

if __name__ == "__main__":
    main()
