"""SQLite storage for Chat Bridge (v2, multi-provider). All data remains on this computer."""
from __future__ import annotations

import hashlib
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

VERSION = "2.0.0"

PROVIDERS = {
    "chatgpt": "ChatGPT",
    "claude": "Claude",
    "gemini": "Gemini",
    "grok": "Grok",
}


def normalize_provider(value: Any) -> str:
    provider = str(value or "chatgpt").strip().lower()
    return provider if provider in PROVIDERS else "chatgpt"


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


_V2_SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    provider TEXT NOT NULL DEFAULT 'chatgpt',
    id TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    url TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    PRIMARY KEY (provider, id)
);
CREATE TABLE IF NOT EXISTS messages (
    provider TEXT NOT NULL DEFAULT 'chatgpt',
    conversation_id TEXT NOT NULL,
    message_key TEXT NOT NULL,
    ordinal INTEGER NOT NULL DEFAULT 0,
    role TEXT NOT NULL CHECK(role IN ('user','assistant')),
    content TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    PRIMARY KEY (provider, conversation_id, message_key),
    FOREIGN KEY (provider, conversation_id) REFERENCES conversations(provider, id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_order
    ON messages(provider, conversation_id, ordinal, captured_at);
CREATE INDEX IF NOT EXISTS idx_messages_content ON messages(content);
CREATE TABLE IF NOT EXISTS actions (
    id TEXT PRIMARY KEY,
    provider TEXT NOT NULL DEFAULT 'chatgpt',
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
"""

# v1 (single-provider) -> v2 (multi-provider). Runs only when the old shape is detected.
_V1_TO_V2 = """
PRAGMA foreign_keys=OFF;
CREATE TABLE conversations_v2 (
    provider TEXT NOT NULL DEFAULT 'chatgpt',
    id TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    url TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    PRIMARY KEY (provider, id)
);
INSERT INTO conversations_v2 (provider, id, title, url, updated_at, last_seen_at)
    SELECT 'chatgpt', id, title, url, updated_at, last_seen_at FROM conversations;
DROP TABLE conversations;
ALTER TABLE conversations_v2 RENAME TO conversations;
CREATE TABLE messages_v2 (
    provider TEXT NOT NULL DEFAULT 'chatgpt',
    conversation_id TEXT NOT NULL,
    message_key TEXT NOT NULL,
    ordinal INTEGER NOT NULL DEFAULT 0,
    role TEXT NOT NULL CHECK(role IN ('user','assistant')),
    content TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    PRIMARY KEY (provider, conversation_id, message_key),
    FOREIGN KEY (provider, conversation_id) REFERENCES conversations(provider, id) ON DELETE CASCADE
);
INSERT INTO messages_v2 (provider, conversation_id, message_key, ordinal, role, content, captured_at)
    SELECT 'chatgpt', conversation_id, message_key, ordinal, role, content, captured_at FROM messages;
DROP TABLE messages;
ALTER TABLE messages_v2 RENAME TO messages;
CREATE TABLE actions_v2 (
    id TEXT PRIMARY KEY,
    provider TEXT NOT NULL DEFAULT 'chatgpt',
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
INSERT INTO actions_v2 (id, provider, conversation_id, message, status, created_at, expires_at,
                        dispatched_at, completed_at, response, error)
    SELECT id, 'chatgpt', conversation_id, message, status, created_at, expires_at,
           dispatched_at, completed_at, response, error FROM actions;
DROP TABLE actions;
ALTER TABLE actions_v2 RENAME TO actions;
PRAGMA foreign_keys=ON;
"""


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}


def init_db(db_path: str | Path) -> None:
    with connect(db_path) as conn:
        existing = _columns(conn, "conversations")
        if existing and "provider" not in existing:
            # v1 database: migrate old tables to the multi-provider shape before creating DDL
            # that references the new provider columns.
            conn.executescript(_V1_TO_V2)
        conn.executescript(_V2_SCHEMA)


def save_snapshot(db_path: str | Path, snapshot: dict[str, Any]) -> dict[str, Any]:
    provider = normalize_provider(snapshot.get("provider"))
    conversation_id = str(snapshot.get("conversation_id", "")).strip()
    if not conversation_id or len(conversation_id) > 200:
        raise ValueError("Invalid or missing conversation_id")
    title = str(snapshot.get("title") or f"Untitled {PROVIDERS[provider]} conversation")[:300]
    url = str(snapshot.get("url") or "")[:2000]
    raw_messages = snapshot.get("messages")
    if not isinstance(raw_messages, list):
        raise ValueError("messages must be an array")
    now = utc_now()
    saved = 0
    with connect(db_path) as conn:
        conn.execute("""INSERT INTO conversations(provider,id,title,url,updated_at,last_seen_at)
            VALUES(?,?,?,?,?,?) ON CONFLICT(provider,id) DO UPDATE SET
            title=excluded.title,url=excluded.url,updated_at=excluded.updated_at,last_seen_at=excluded.last_seen_at""",
            (provider, conversation_id, title, url, now, now))
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
            conn.execute("""INSERT INTO messages(provider,conversation_id,message_key,ordinal,role,content,captured_at)
                VALUES(?,?,?,?,?,?,?) ON CONFLICT(provider,conversation_id,message_key) DO UPDATE SET
                ordinal=excluded.ordinal,role=excluded.role,content=excluded.content,captured_at=excluded.captured_at""",
                (provider, conversation_id, key, ordinal, role, content, now))
            saved += 1
        total = conn.execute("SELECT COUNT(*) FROM messages WHERE provider=? AND conversation_id=?",
                             (provider, conversation_id)).fetchone()[0]
    return {"provider": provider, "saved_messages_in_snapshot": saved, "stored_message_count": total}


def _provider_filter(provider: str | None, param: str = "c.provider") -> tuple[str, list]:
    if not provider:
        return "", []
    return f" WHERE {param}=?", [normalize_provider(provider)]


def list_conversations(db_path: str | Path, limit: int = 30, provider: str | None = None) -> list[dict[str, Any]]:
    limit = max(1, min(int(limit), 200))
    where, params = _provider_filter(provider)
    with connect(db_path) as conn:
        rows = conn.execute(f"""SELECT c.provider,c.id,c.title,c.url,c.updated_at,
            COUNT(m.message_key) AS message_count,
            (SELECT SUBSTR(m.content,1,700) FROM messages m WHERE m.provider=c.provider AND m.conversation_id=c.id
             ORDER BY m.ordinal DESC,m.captured_at DESC LIMIT 1) AS last_message
            FROM conversations c LEFT JOIN messages m ON m.provider=c.provider AND m.conversation_id=c.id
            {where}
            GROUP BY c.provider,c.id ORDER BY c.last_seen_at DESC LIMIT ?""",
            [*params, limit]).fetchall()
        return [dict(row) for row in rows]


def search_messages(db_path: str | Path, query: str, limit: int = 30, provider: str | None = None) -> list[dict[str, Any]]:
    query = str(query).strip()
    if not query:
        raise ValueError("query cannot be empty")
    limit = max(1, min(int(limit), 100))
    pattern = f"%{query[:300]}%"
    where, params = _provider_filter(provider, "c.provider")
    where = where.replace(" WHERE", " AND", 1)
    with connect(db_path) as conn:
        rows = conn.execute(f"""SELECT c.provider,m.conversation_id,c.title,m.role,m.content,m.ordinal,m.captured_at
            FROM messages m JOIN conversations c ON c.provider=m.provider AND c.id=m.conversation_id
            WHERE m.content LIKE ? COLLATE NOCASE {where}
            ORDER BY c.last_seen_at DESC,m.ordinal DESC LIMIT ?""", (pattern, *params, limit)).fetchall()
        return [dict(row) for row in rows]


def find_conversation(db_path: str | Path, conversation_id: str) -> dict[str, Any] | None:
    """Look a conversation up by id alone; returns the most recently updated match (across providers)."""
    with connect(db_path) as conn:
        row = conn.execute("""SELECT provider,id,title,url,updated_at,last_seen_at FROM conversations
            WHERE id=? ORDER BY updated_at DESC LIMIT 1""", (conversation_id,)).fetchone()
        return dict(row) if row else None


def read_conversation(db_path: str | Path, conversation_id: str, limit: int = 100,
                      provider: str | None = None) -> dict[str, Any] | None:
    limit = max(1, min(int(limit), 500))
    with connect(db_path) as conn:
        if provider:
            provider = normalize_provider(provider)
            conversation = conn.execute(
                "SELECT * FROM conversations WHERE provider=? AND id=?", (provider, conversation_id)).fetchone()
        else:
            conversation = conn.execute(
                "SELECT * FROM conversations WHERE id=? ORDER BY updated_at DESC LIMIT 1", (conversation_id,)).fetchone()
        if not conversation:
            return None
        conversation = dict(conversation)
        rows = conn.execute("""SELECT role,content,ordinal,captured_at FROM messages
            WHERE provider=? AND conversation_id=? ORDER BY ordinal DESC,captured_at DESC LIMIT ?""",
            (conversation["provider"], conversation_id, limit)).fetchall()
        messages = [dict(row) for row in reversed(rows)]
        total = conn.execute("SELECT COUNT(*) FROM messages WHERE provider=? AND conversation_id=?",
                             (conversation["provider"], conversation_id)).fetchone()[0]
        return {"conversation": conversation, "messages": messages,
                "stored_message_count": total,
                "note": f"Only messages rendered in the {PROVIDERS[conversation['provider']]} page were captured. "
                        "This may be a partial conversation if older messages were not loaded in the page."}


def provider_stats(db_path: str | Path) -> dict[str, dict[str, Any]]:
    with connect(db_path) as conn:
        rows = conn.execute("""SELECT c.provider, COUNT(DISTINCT c.id) AS conversations,
            COUNT(m.message_key) AS messages, MAX(c.updated_at) AS last_updated
            FROM conversations c LEFT JOIN messages m ON m.provider=c.provider AND m.conversation_id=c.id
            GROUP BY c.provider""").fetchall()
        return {row["provider"]: {"label": PROVIDERS.get(row["provider"], row["provider"]), **dict(row)}
                for row in rows}


def queue_action(db_path: str | Path, conversation_id: str, message: str, timeout_seconds: int = 90,
                 provider: str | None = None) -> str:
    import uuid
    if provider:
        provider = normalize_provider(provider)
    else:
        stored = find_conversation(db_path, conversation_id)
        if not stored:
            raise ValueError("Conversation not found in local archive. Open it in the browser first "
                             "so Chat Bridge can capture it.")
        provider = stored["provider"]
    action_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    expires = now + timedelta(seconds=max(15, min(int(timeout_seconds), 120)))
    with connect(db_path) as conn:
        exists = conn.execute("SELECT 1 FROM conversations WHERE provider=? AND id=?",
                              (provider, conversation_id)).fetchone()
        if not exists:
            raise ValueError(f"Conversation not found in local archive ({PROVIDERS[provider]}). "
                             "Open it in the browser first so Chat Bridge can capture it.")
        conn.execute("""INSERT INTO actions(id,provider,conversation_id,message,status,created_at,expires_at)
            VALUES(?,?,?,?,'pending',?,?)""",
            (action_id, provider, conversation_id, message[:12000],
             now.isoformat(timespec="seconds"), expires.isoformat(timespec="seconds")))
    return action_id


def claim_action(db_path: str | Path, conversation_id: str, allow_agent_send: bool,
                 provider: str | None = None) -> dict[str, Any] | None:
    if not allow_agent_send:
        return None
    provider = normalize_provider(provider)
    now = utc_now()
    with connect(db_path) as conn:
        conn.execute("UPDATE actions SET status='expired',error='Action expired before browser dispatch.' "
                     "WHERE status='pending' AND expires_at<=?", (now,))
        row = conn.execute("""SELECT id,provider,conversation_id,message,expires_at FROM actions
            WHERE status='pending' AND provider=? AND conversation_id=? AND expires_at>?
            ORDER BY created_at LIMIT 1""", (provider, conversation_id, now)).fetchone()
        if not row:
            return None
        result = dict(row)
        changed = conn.execute(
            "UPDATE actions SET status='dispatched',dispatched_at=? WHERE id=? AND status='pending'",
            (now, result["id"])).rowcount
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


def conversation_count(db_path: str | Path, provider: str | None = None) -> int:
    where, params = _provider_filter(provider, "provider")
    with connect(db_path) as conn:
        return int(conn.execute(f"SELECT COUNT(*) FROM conversations{where}", params).fetchone()[0])
