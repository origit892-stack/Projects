"""SQLite storage for Chat Bridge. All data remains on this computer."""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def connect(db_path: str | Path):
    path = Path(db_path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: str | Path) -> None:
    with connect(db_path) as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL DEFAULT '',
            url TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS messages (
            conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            message_key TEXT NOT NULL,
            ordinal INTEGER NOT NULL DEFAULT 0,
            role TEXT NOT NULL CHECK(role IN ('user','assistant')),
            content TEXT NOT NULL,
            captured_at TEXT NOT NULL,
            PRIMARY KEY(conversation_id, message_key)
        );
        CREATE INDEX IF NOT EXISTS idx_messages_conversation_order
            ON messages(conversation_id, ordinal, captured_at);
        CREATE INDEX IF NOT EXISTS idx_messages_content ON messages(content);
        CREATE TABLE IF NOT EXISTS actions (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            dispatched_at TEXT,
            completed_at TEXT,
            response TEXT,
            error TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_actions_status ON actions(status, created_at);
        """)


def save_snapshot(db_path: str | Path, snapshot: dict[str, Any]) -> dict[str, Any]:
    conversation_id = str(snapshot.get("conversation_id", "")).strip()
    if not conversation_id or len(conversation_id) > 200:
        raise ValueError("Invalid or missing conversation_id")
    title = str(snapshot.get("title") or "Untitled ChatGPT conversation")[:300]
    url = str(snapshot.get("url") or "")[:2000]
    raw_messages = snapshot.get("messages")
    if not isinstance(raw_messages, list):
        raise ValueError("messages must be an array")
    now = utc_now()
    saved = 0
    with connect(db_path) as conn:
        conn.execute("""INSERT INTO conversations(id,title,url,updated_at,last_seen_at)
            VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
            title=excluded.title,url=excluded.url,updated_at=excluded.updated_at,last_seen_at=excluded.last_seen_at""",
            (conversation_id, title, url, now, now))
        for index, item in enumerate(raw_messages[:500]):
            if not isinstance(item, dict):
                continue
            role = item.get("role")
            if role not in ("user", "assistant"):
                continue
            content = str(item.get("content") or "").strip()
            if not content:
                continue
            content = content[:60000]
            key = str(item.get("key") or "").strip()[:300]
            if not key:
                digest = hashlib.sha256(f"{role}\0{content}".encode("utf-8")).hexdigest()
                key = f"hash:{digest}"
            ordinal = item.get("ordinal", index)
            try:
                ordinal = max(0, min(int(ordinal), 10000))
            except (TypeError, ValueError):
                ordinal = index
            conn.execute("""INSERT INTO messages(conversation_id,message_key,ordinal,role,content,captured_at)
                VALUES(?,?,?,?,?,?) ON CONFLICT(conversation_id,message_key) DO UPDATE SET
                ordinal=excluded.ordinal,role=excluded.role,content=excluded.content,captured_at=excluded.captured_at""",
                (conversation_id, key, ordinal, role, content, now))
            saved += 1
        total = conn.execute("SELECT COUNT(*) FROM messages WHERE conversation_id=?", (conversation_id,)).fetchone()[0]
    return {"saved_messages_in_snapshot": saved, "stored_message_count": total}


def list_conversations(db_path: str | Path, limit: int = 30) -> list[dict[str, Any]]:
    limit = max(1, min(int(limit), 200))
    with connect(db_path) as conn:
        rows = conn.execute("""SELECT c.id,c.title,c.url,c.updated_at,
            COUNT(m.message_key) AS message_count,
            (SELECT SUBSTR(content,1,700) FROM messages WHERE conversation_id=c.id ORDER BY ordinal DESC,captured_at DESC LIMIT 1) AS last_message
            FROM conversations c LEFT JOIN messages m ON m.conversation_id=c.id
            GROUP BY c.id ORDER BY c.last_seen_at DESC LIMIT ?""", (limit,)).fetchall()
        return [dict(row) for row in rows]


def search_messages(db_path: str | Path, query: str, limit: int = 30) -> list[dict[str, Any]]:
    query = str(query).strip()
    if not query:
        raise ValueError("query cannot be empty")
    limit = max(1, min(int(limit), 100))
    pattern = f"%{query[:300]}%"
    with connect(db_path) as conn:
        rows = conn.execute("""SELECT m.conversation_id,c.title,m.role,m.content,m.ordinal,m.captured_at
            FROM messages m JOIN conversations c ON c.id=m.conversation_id
            WHERE m.content LIKE ? COLLATE NOCASE
            ORDER BY c.last_seen_at DESC,m.ordinal DESC LIMIT ?""", (pattern, limit)).fetchall()
        return [dict(row) for row in rows]


def read_conversation(db_path: str | Path, conversation_id: str, limit: int = 100) -> dict[str, Any] | None:
    limit = max(1, min(int(limit), 500))
    with connect(db_path) as conn:
        conversation = conn.execute("SELECT * FROM conversations WHERE id=?", (conversation_id,)).fetchone()
        if not conversation:
            return None
        rows = conn.execute("""SELECT role,content,ordinal,captured_at FROM messages
            WHERE conversation_id=? ORDER BY ordinal DESC,captured_at DESC LIMIT ?""",
            (conversation_id, limit)).fetchall()
        messages = [dict(row) for row in reversed(rows)]
        total = conn.execute("SELECT COUNT(*) FROM messages WHERE conversation_id=?", (conversation_id,)).fetchone()[0]
        return {"conversation": dict(conversation), "messages": messages,
                "stored_message_count": total,
                "note": "Only messages rendered in ChatGPT's page were captured. This may be a partial conversation if older messages were not loaded in the page."}


def queue_action(db_path: str | Path, conversation_id: str, message: str, timeout_seconds: int = 90) -> str:
    import uuid
    action_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    expires = now + timedelta(seconds=max(15, min(int(timeout_seconds), 120)))
    with connect(db_path) as conn:
        exists = conn.execute("SELECT 1 FROM conversations WHERE id=?", (conversation_id,)).fetchone()
        if not exists:
            raise ValueError("Conversation not found in local archive. Open it in ChatGPT first so Chat Bridge can capture it.")
        conn.execute("""INSERT INTO actions(id,conversation_id,message,status,created_at,expires_at)
            VALUES(?,?,?,'pending',?,?)""",
            (action_id, conversation_id, message[:12000], now.isoformat(timespec="seconds"), expires.isoformat(timespec="seconds")))
    return action_id


def claim_action(db_path: str | Path, conversation_id: str, allow_agent_send: bool) -> dict[str, Any] | None:
    if not allow_agent_send:
        return None
    now = utc_now()
    with connect(db_path) as conn:
        conn.execute("UPDATE actions SET status='expired',error='Action expired before browser dispatch.' WHERE status='pending' AND expires_at<=?", (now,))
        row = conn.execute("""SELECT id,conversation_id,message,expires_at FROM actions
            WHERE status='pending' AND conversation_id=? AND expires_at>? ORDER BY created_at LIMIT 1""",
            (conversation_id, now)).fetchone()
        if not row:
            return None
        result = dict(row)
        changed = conn.execute("UPDATE actions SET status='dispatched',dispatched_at=? WHERE id=? AND status='pending'", (now, result['id'])).rowcount
        return result if changed else None


def complete_action(db_path: str | Path, action_id: str, status: str, response: str = "", error: str = "") -> bool:
    if status not in ("completed", "failed"):
        raise ValueError("status must be completed or failed")
    with connect(db_path) as conn:
        changed = conn.execute("""UPDATE actions SET status=?,response=?,error=?,completed_at=?
            WHERE id=? AND status='dispatched'""",
            (status, response[:60000], error[:2000], utc_now(), action_id)).rowcount
        return bool(changed)


def get_action(db_path: str | Path, action_id: str) -> dict[str, Any] | None:
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM actions WHERE id=?", (action_id,)).fetchone()
        return dict(row) if row else None


def conversation_count(db_path: str | Path) -> int:
    with connect(db_path) as conn:
        return int(conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0])
