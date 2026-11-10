#!/usr/bin/env python3
"""MCP stdio server shared by Hermes and OpenCode."""
from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from db import (complete_action, conversation_count, get_action, init_db, list_conversations,
                queue_action, read_conversation, search_messages)

CONFIG_PATH = Path(os.environ.get("CHAT_BRIDGE_CONFIG", "~/.chat-bridge/config.json")).expanduser()
if not CONFIG_PATH.exists():
    raise SystemExit(f"Chat Bridge config not found: {CONFIG_PATH}. Run install_mac.sh first.")
CONFIG = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
DB_PATH = str(Path(CONFIG.get("db_path", "~/.chat-bridge/chat-bridge.sqlite3")).expanduser())
init_db(DB_PATH)

mcp = FastMCP("chat-bridge")


@mcp.tool()
def chatbridge_status() -> str:
    """Show whether the local Chat Bridge archive exists and how many conversations it contains."""
    conversations = list_conversations(DB_PATH, 1)
    return json.dumps({"storage": "local SQLite", "database": DB_PATH,
                       "saved_conversations": conversation_count(DB_PATH),
                       "latest_conversation": conversations[0] if conversations else None}, ensure_ascii=False, default=str)


@mcp.tool()
def chatbridge_list_conversations(limit: int = 30) -> str:
    """List recently captured ChatGPT conversations. Returns IDs, titles, counts and last-message previews."""
    return json.dumps(list_conversations(DB_PATH, limit), ensure_ascii=False, default=str)


@mcp.tool()
def chatbridge_search_messages(query: str, limit: int = 20) -> str:
    """Search locally archived ChatGPT message text. Use this to find earlier decisions or project discussions."""
    rows = search_messages(DB_PATH, query, min(limit, 50))
    for row in rows:
        if len(row["content"]) > 10000:
            row["content"] = row["content"][:10000] + "… [message truncated for tool output]"
    return json.dumps(rows, ensure_ascii=False, default=str)


@mcp.tool()
def chatbridge_read_conversation(conversation_id: str, limit: int = 80) -> str:
    """Read a captured conversation by ID in chronological order. The archive can be partial if not all older messages were loaded in the browser."""
    result = read_conversation(DB_PATH, conversation_id, min(limit, 150))
    if not result:
        return json.dumps({"error": "Conversation not found", "conversation_id": conversation_id}, ensure_ascii=False)
    budget = 90000
    compact = []
    for item in result["messages"]:
        message = dict(item)
        content = message["content"]
        allowance = min(18000, budget)
        if allowance <= 0:
            break
        if len(content) > allowance:
            message["content"] = content[:allowance] + "… [message truncated for tool output]"
        compact.append(message)
        budget -= min(len(content), allowance)
    result["messages"] = compact
    result["returned_message_count"] = len(compact)
    if len(compact) < result["stored_message_count"]:
        result["output_note"] = "Tool output was limited to keep the context manageable; call again with a smaller time range or use chatbridge_search_messages for targeted retrieval."
    return json.dumps(result, ensure_ascii=False, default=str)


@mcp.tool()
async def chatbridge_send_message(conversation_id: str, message: str, timeout_seconds: int = 90) -> str:
    """Send a message into the matching currently open ChatGPT browser conversation and wait for its reply. Requires the Chrome extension's 'Allow Agent to send messages' switch to be enabled and that exact conversation to be open."""
    if not message.strip():
        return json.dumps({"error": "Message cannot be empty."}, ensure_ascii=False)
    timeout_seconds = max(15, min(int(timeout_seconds), 120))
    try:
        action_id = queue_action(DB_PATH, conversation_id, message, timeout_seconds)
    except ValueError as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)

    deadline = time.time() + timeout_seconds + 3
    while time.time() < deadline:
        action = get_action(DB_PATH, action_id)
        if not action:
            return json.dumps({"error": "Queued action disappeared.", "action_id": action_id}, ensure_ascii=False)
        if action["status"] == "completed":
            return json.dumps({"ok": True, "conversation_id": conversation_id,
                               "assistant_response": action.get("response", "")}, ensure_ascii=False)
        if action["status"] in ("failed", "expired"):
            return json.dumps({"error": action.get("error") or f"Action {action['status']}.",
                               "status": action["status"], "action_id": action_id}, ensure_ascii=False)
        await asyncio.sleep(0.5)

    with __import__("contextlib").suppress(Exception):
        complete_action(DB_PATH, action_id, "failed", error=(
            "Timed out waiting for the browser. Keep the target conversation open, start the local bridge, "
            "and enable 'Allow Agent to send messages' in the extension."
        ))
    return json.dumps({"error": "Timed out waiting for ChatGPT in the browser. Check the open tab and extension permission.",
                       "action_id": action_id}, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")
