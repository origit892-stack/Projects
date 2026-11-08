#!/usr/bin/env python3

import base64
import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import urllib.error

PROJECT = "/Users/Ori/Documents/Projects/BunkerGame"
SERVER = "http://127.0.0.1:4096"

def get_auth():
    out = subprocess.run(
        ["/bin/ps", "-ax", "-o", "pid=", "-o", "command="],
        text=True,
        capture_output=True,
        check=True,
    ).stdout

    pid = None

    for line in out.splitlines():
        if "opencode serve" in line:
            pid = line.strip().split(None, 1)[0]
            break

    if not pid:
        raise RuntimeError("OpenCode server not running")

    env = subprocess.run(
        ["/bin/ps", "eww", "-p", pid],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.splitlines()[-1]

    user = None
    password = None

    for item in env.split():
        if item.startswith("OPENCODE_SERVER_USERNAME="):
            user = item.split("=", 1)[1]

        if item.startswith("OPENCODE_SERVER_PASSWORD="):
            password = item.split("=", 1)[1]

    if not user or not password:
        raise RuntimeError("OpenCode authentication unavailable")

    return user, password

USER, PASSWORD = get_auth()

AUTH = base64.b64encode(
    f"{USER}:{PASSWORD}".encode()
).decode()

class OpenCodeTransportError(RuntimeError):
    pass


class OpenCodeMalformedResponseError(RuntimeError):
    pass


def request(method, path, body=None, timeout=60, retries=4, backoff=1.5):
    headers = {
        "Accept": "application/json",
        "Authorization": "Basic " + AUTH,
    }
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"

    url = SERVER + path
    last_error = None
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                status = getattr(r, "status", None)
                if not raw:
                    if status == 204:
                        return None
                    raise OpenCodeMalformedResponseError(
                        f"Empty response from {method} {path} with HTTP {status}"
                    )
                try:
                    return json.loads(raw.decode())
                except (UnicodeDecodeError, json.JSONDecodeError) as e:
                    preview = raw[:500].decode(errors="replace")
                    raise OpenCodeMalformedResponseError(
                        f"Malformed JSON from {method} {path}: {e}; preview={preview!r}"
                    ) from e
        except urllib.error.HTTPError as e:
            raw = e.read().decode(errors="replace")
            raise RuntimeError(f"HTTP {e.code} {method} {path}: {raw}") from e
        except OpenCodeMalformedResponseError:
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            last_error = e
            if attempt >= retries:
                break
            delay = backoff * (2 ** (attempt - 1))
            print(
                f"BLOXBOT_API_TRANSPORT_RETRY={attempt}/{retries} "
                f"delay={delay:.1f}s error={e}",
                flush=True,
            )
            time.sleep(delay)

    raise OpenCodeTransportError(
        f"Transport failure after {retries} attempts for {method} {path}: {last_error}"
    )

def q(path):
    return (
        path
        + "?directory="
        + urllib.parse.quote(PROJECT, safe="")
    )

def create_session():
    body = {
        "title": "Environment Director API specialist",
        "permission": [
            {
                "permission": "*",
                "pattern": "*",
                "action": "allow",
            }
        ],
    }

    session = request(
        "POST",
        q("/session"),
        body,
    )

    if session.get("directory") != PROJECT:
        raise RuntimeError(
            "Wrong session directory: "
            + repr(session.get("directory"))
        )

    return session["id"]

def submit_async(sid, prompt):
    body = {
        "variant": "max",
        "parts": [
            {
                "type": "text",
                "text": prompt,
            }
        ],
    }

    request(
        "POST",
        q(f"/session/{sid}/prompt_async"),
        body,
    )

def permissions(sid):
    result = request(
        "GET",
        q("/permission"),
    )

    return [
        x for x in (result or [])
        if x.get("sessionID") == sid
    ]

def approve_permissions(sid):
    pending = permissions(sid)

    for item in pending:
        rid = item.get("id")

        if not rid:
            continue

        print(
            "BLOXBOT_PERMISSION_AUTO_APPROVE="
            + rid,
            flush=True,
        )

        request(
            "POST",
            q(f"/permission/{rid}/reply"),
            {
                "reply": "always",
                "message": (
                    "Authorized Environment Director "
                    "specialist session."
                ),
            },
        )

def questions(sid):
    result = request(
        "GET",
        q("/question"),
    )

    return [
        x for x in (result or [])
        if x.get("sessionID") == sid
    ]

def status(sid):
    all_status = request(
        "GET",
        q("/session/status"),
    ) or {}

    return all_status.get(
        sid,
        {"type": "idle"},
    )

def messages(sid):
    return request(
        "GET",
        q(f"/session/{sid}/message")
        + "&limit=100",
    ) or []

def assistant_text(sid):
    chunks = []

    for msg in messages(sid):
        info = msg.get("info", {})

        if info.get("role") != "assistant":
            continue

        for part in msg.get("parts", []):
            if part.get("type") == "text":
                text = part.get("text", "")

                if text:
                    chunks.append(text)

    return "\n".join(chunks)

def run(prompt, timeout):
    sid = create_session()

    print(
        "BLOXBOT_API_SESSION=" + sid,
        flush=True,
    )

    print(
        "BLOXBOT_API_DIRECTORY=" + PROJECT,
        flush=True,
    )

    submit_async(sid, prompt)

    print(
        "BLOXBOT_PROMPT_ACCEPTED=PASS",
        flush=True,
    )

    started = time.monotonic()
    seen_busy = False
    seen_tool_states = {}
    last_heartbeat = -30
    last_activity = 0

    while True:
        elapsed = int(
            time.monotonic() - started
        )

        # timeout is an inactivity/stall timeout, NOT a total wall-clock limit.
        # A healthy long-running session may continue indefinitely while new
        # tool activity is observed.
        quiet = elapsed - last_activity

        if quiet >= timeout:
            request(
                "POST",
                q(f"/session/{sid}/abort"),
                {},
            )

            raise RuntimeError(
                f"BloxBot stalled: no new tool activity for {timeout}s"
            )

        approve_permissions(sid)

        pending_questions = questions(sid)

        if pending_questions:
            print(
                "BLOXBOT_PENDING_QUESTION="
                + json.dumps(
                    pending_questions,
                    ensure_ascii=False,
                ),
                flush=True,
            )

            request(
                "POST",
                q(f"/session/{sid}/abort"),
                {},
            )

            raise RuntimeError(
                "Agent requested human input"
            )

        current = status(sid)
        state = current.get("type", "unknown")

        if state in ("busy", "retry"):
            seen_busy = True

        current_messages = messages(sid)

        for msg in current_messages:
            if msg.get("info", {}).get("role") != "assistant":
                continue

            for part in msg.get("parts", []):
                if part.get("type") != "tool":
                    continue

                tool_id = part.get("id")

                if tool_id in seen_tool_states:
                    old_state = seen_tool_states[tool_id]
                else:
                    old_state = None

                tool_state = part.get("state", {})
                tool_status = tool_state.get("status", "unknown")

                state_key = (tool_status, tool_state.get("title"))

                if old_state != state_key:
                    seen_tool_states[tool_id] = state_key

                    title = tool_state.get("title") or ""
                    tool_name = part.get("tool") or "tool"

                    print(
                        f"[{elapsed:04d}s] "
                        f"{tool_name} "
                        f"{tool_status.upper()} "
                        f"{title}",
                        flush=True,
                    )

                    if tool_status == "error":
                        print(
                            "TOOL_ERROR="
                            + str(tool_state.get("error")),
                            flush=True,
                        )

                    last_activity = elapsed

        if elapsed - last_heartbeat >= 30:
            quiet = elapsed - last_activity

            print(
                f"[{elapsed:04d}s] "
                f"STATUS={state} "
                f"QUIET={quiet}s",
                flush=True,
            )

            last_heartbeat = elapsed

        if state == "idle" and seen_busy:
            break

        time.sleep(2)

    text = assistant_text(sid)

    if text:
        print(text, flush=True)

    print(
        "BLOXBOT_API_COMPLETE=PASS",
        flush=True,
    )

    return text

def main():
    if len(sys.argv) < 2:
        raise SystemExit(
            "usage: bloxbot_api.py PROMPT_FILE [TIMEOUT]"
        )

    prompt = open(
        sys.argv[1],
        "r",
        encoding="utf-8",
    ).read()

    timeout = (
        int(sys.argv[2])
        if len(sys.argv) > 2
        else 900
    )

    run(prompt, timeout)

if __name__ == "__main__":
    main()
