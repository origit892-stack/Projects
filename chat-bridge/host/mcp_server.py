#!/usr/bin/env python3
"""Minimal local MCP server exposing the local Chat Bridge v2 archive."""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import db

HOST = "127.0.0.1"
PORT = 8765
CONFIG = Path.home() / ".chat-bridge" / "config.json"
DB = Path.home() / ".chat-bridge" / "chat-bridge.sqlite3"


def load_token() -> str:
    try:
        return str(json.loads(CONFIG.read_text(encoding="utf-8")).get("token") or "").strip()
    except Exception:
        return ""


def daemon_get(path: str, timeout: float = 5.0) -> dict[str, Any]:
    token = load_token()
    request = urllib.request.Request(f"http://{HOST}:{PORT}{path}",
                                     headers={"Authorization": f"Bearer {token}",
                                              "X-Chat-Bridge-Token": token})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def daemon_health() -> dict[str, Any]:
    """Prefer the tokenless v2 /healthz; fall back to the token-gated v1 /health."""
    try:
        return daemon_get("/healthz", timeout=2.0)
    except Exception:
        return {"ok": True, **daemon_get("/health", timeout=2.0)}


def status_payload() -> dict[str, Any]:
    try:
        health = daemon_health()
    except Exception as e:
        return {"ok": False, "daemon": "offline", "error": str(e),
                "hint": "Start the local daemon from the project folder (./start.command or the daemon command in the README)."}
    providers = {}
    try:
        providers = daemon_get("/providers", timeout=2.0).get("providers", {})
    except Exception:
        # v1 daemon has no /providers — fall back to direct DB stats.
        providers = {p: {"label": info["label"], "conversations": info["conversations"],
                         "messages": info["messages"], "last_updated": info["last_updated"]}
                     for p, info in db.provider_stats(DB).items()}
    return {"ok": True, "daemon": "running", **health, "providers": providers}


def status() -> dict[str, Any]:
    return status_payload()


def list_conversations(limit: int = 30, provider: str = "") -> list[dict[str, Any]]:
    return db.list_conversations(DB, limit=limit, provider=provider or None)


def read_conversation(conversation_id: str, limit: int = 100, provider: str = "") -> dict[str, Any] | None:
    return db.read_conversation(DB, conversation_id, limit=limit, provider=provider or None)


def search_messages(query: str, limit: int = 30, provider: str = "") -> list[dict[str, Any]]:
    return db.search_messages(DB, query, limit=limit, provider=provider or None)


def send_message(conversation_id: str, message: str, provider: str = "", timeout: int = 90) -> dict[str, Any]:
    if not str(message).strip():
        raise ValueError("message cannot be empty")
    try:
        action_id = db.queue_action(DB, conversation_id, message, timeout, provider=provider or None)
    except ValueError:
        raise
    return {"status": "queued", "action_id": action_id,
            "message": "Delivered to the local daemon queue. The Chrome extension will send it when the matching "
                       "provider tab is visible and 'Allow Agent to send messages' is enabled. Poll this action id "
                       "with chatbridge_status or re-read the conversation."}


TOOLS = [
    {"name": "chatbridge_status",
     "description": "Report whether the local Chat Bridge daemon is running and summarize stored conversations per provider.",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}, "fn": status},
    {"name": "chatbridge_provider_status",
     "description": "Per-provider live status: stored conversation/message counts, last capture time, and the latest "
                    "capture diagnostic from each provider's browser tab (capture_failed + reason when a page layout "
                    "changed).",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}, "fn": status_payload},
    {"name": "chatbridge_list_conversations",
     "description": "List locally archived provider conversations (ChatGPT, Claude, Gemini, Grok), most recently "
                    "updated first. provider is optional (empty = all providers).",
     "inputSchema": {"type": "object",
                     "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 100},
                                    "provider": {"type": "string",
                                                 "description": "Optional: chatgpt | claude | gemini | grok. Empty = all."}},
                     "additionalProperties": False}, "fn": list_conversations},
    {"name": "chatbridge_read_conversation",
     "description": "Read locally captured messages from one provider conversation. provider is optional; when "
                    "omitted the most recently updated conversation with that id is used.",
     "inputSchema": {"type": "object",
                     "properties": {"conversation_id": {"type": "string"},
                                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                                    "provider": {"type": "string"}},
                     "required": ["conversation_id"], "additionalProperties": False}, "fn": read_conversation},
    {"name": "chatbridge_search_messages",
     "description": "Search the local provider conversation archive by text.",
     "inputSchema": {"type": "object",
                     "properties": {"query": {"type": "string"},
                                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                                    "provider": {"type": "string"}},
                     "required": ["query"], "additionalProperties": False}, "fn": search_messages},
    {"name": "chatbridge_send_message",
     "description": "Queue a message for the agent to send in an open provider conversation. provider is optional; "
                    "it is inferred from the local archive when omitted. The browser tab must be visible and "
                    "'Allow Agent to send messages' must be enabled.",
     "inputSchema": {"type": "object",
                     "properties": {"conversation_id": {"type": "string"},
                                    "message": {"type": "string"},
                                    "provider": {"type": "string"},
                                    "timeout": {"type": "integer", "minimum": 15, "maximum": 120,
                                                "description": "Seconds before the queued action expires"}},
                     "required": ["conversation_id", "message"], "additionalProperties": False}, "fn": send_message},
]


def tools():
    return [{"name": tool["name"], "description": tool["description"], "inputSchema": tool["inputSchema"]}
            for tool in TOOLS]


def call(name: str, arguments: dict[str, Any]) -> Any:
    for tool in TOOLS:
        if tool["name"] == name:
            return tool["fn"](**(arguments or {}))
    raise ValueError(f"Unknown tool: {name}")


def rpc(payload: dict[str, Any]) -> dict[str, Any] | None:
    request_id = payload.get("id")
    method = payload.get("method")
    params = payload.get("params") or {}
    if method == "initialize":
        result = {"protocolVersion": "2025-03-26",
                  "capabilities": {"tools": {"listChanged": False}},
                  "serverInfo": {"name": "chat-bridge-v2", "version": db.VERSION}}
        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools()}}
    if method == "tools/call":
        name = params.get("name")
        try:
            output = call(name, params.get("arguments") or {})
            content = [{"type": "text", "text": json.dumps(output, ensure_ascii=False, indent=2)}]
            return {"jsonrpc": "2.0", "id": request_id,
                    "result": {"content": content, "structuredContent": output if isinstance(output, (dict, list)) else {"value": output}}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": request_id,
                    "result": {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True}}
    if request_id is None:
        return None
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}


def main() -> None:
    print(json.dumps({"server": "chat-bridge-v2", "version": db.VERSION, "db": str(DB),
                      "daemon": f"http://{HOST}:{PORT}"}), flush=True)
    db.init_db(DB)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            response = rpc(json.loads(line))
        except json.JSONDecodeError:
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        if response is not None:
            print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
