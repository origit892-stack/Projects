import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import db


def make_v1_database(path: Path) -> None:
    """Create a database in the original v1 (single-provider) shape."""
    conn = sqlite3.connect(path)
    conn.executescript("""
    CREATE TABLE conversations (
        id TEXT PRIMARY KEY, title TEXT NOT NULL DEFAULT '', url TEXT NOT NULL DEFAULT '',
        updated_at TEXT NOT NULL, last_seen_at TEXT NOT NULL
    );
    CREATE TABLE messages (
        conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
        message_key TEXT NOT NULL, ordinal INTEGER NOT NULL DEFAULT 0,
        role TEXT NOT NULL CHECK(role IN ('user','assistant')), content TEXT NOT NULL,
        captured_at TEXT NOT NULL,
        PRIMARY KEY(conversation_id, message_key)
    );
    CREATE INDEX idx_messages_conversation_order ON messages(conversation_id, ordinal, captured_at);
    CREATE INDEX idx_messages_content ON messages(content);
    CREATE TABLE actions (
        id TEXT PRIMARY KEY, conversation_id TEXT NOT NULL, message TEXT NOT NULL,
        status TEXT NOT NULL, created_at TEXT NOT NULL, expires_at TEXT NOT NULL,
        dispatched_at TEXT, completed_at TEXT, response TEXT, error TEXT
    );
    CREATE INDEX idx_actions_status ON actions(status, created_at);
    """)
    conn.execute("INSERT INTO conversations VALUES ('v1-conv', 'V1 Title', 'https://chatgpt.com/c/v1-conv', '2026-01-01T00:00:00', '2026-01-01T00:00:00')")
    conn.execute("INSERT INTO messages VALUES ('v1-conv', 'k1', 0, 'user', 'legacy user text', '2026-01-01T00:00:00')")
    conn.execute("INSERT INTO messages VALUES ('v1-conv', 'k2', 1, 'assistant', 'legacy assistant text', '2026-01-01T00:00:00')")
    conn.commit()
    conn.close()


class DbTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "bridge.sqlite3"
        db.init_db(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    # ---- v1 semantics (default provider = chatgpt) ----

    def test_snapshot_upsert_is_idempotent(self):
        payload = {
            "conversation_id": "abc",
            "title": "Test Chat",
            "url": "https://chatgpt.com/c/abc",
            "messages": [
                {"key": "m1", "role": "user", "content": "Hello", "ordinal": 0},
                {"key": "m2", "role": "assistant", "content": "Hi there", "ordinal": 1},
            ],
        }
        first = db.save_snapshot(self.path, payload)
        second = db.save_snapshot(self.path, payload)
        self.assertEqual(first["saved_messages_in_snapshot"], 2)
        self.assertEqual(first["stored_message_count"], 2)
        self.assertEqual(second["stored_message_count"], 2)
        self.assertEqual(db.conversation_count(self.path), 1)

    def test_list_read_search(self):
        db.save_snapshot(self.path, {
            "conversation_id": "abc", "title": "Findable", "url": "u",
            "messages": [{"key": "m1", "role": "user", "content": "zebra crossing", "ordinal": 0}]})
        db.save_snapshot(self.path, {
            "conversation_id": "def", "title": "Other", "url": "u",
            "messages": [{"key": "m1", "role": "user", "content": "nothing here", "ordinal": 0}]})
        rows = db.list_conversations(self.path)
        self.assertEqual(len(rows), 2)
        found = db.search_messages(self.path, "zebra")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["conversation_id"], "abc")
        conversation = db.read_conversation(self.path, "abc")
        self.assertEqual(len(conversation["messages"]), 1)
        self.assertEqual(conversation["conversation"]["title"], "Findable")

    def test_action_lifecycle(self):
        db.save_snapshot(self.path, {"conversation_id": "abc", "messages": [{"key": "m1", "role": "user", "content": "x"}]})
        action_id = db.queue_action(self.path, "abc", "say hello", 30)
        with self.assertRaises(ValueError):
            db.queue_action(self.path, "missing", "say hi")
        claimed = db.claim_action(self.path, "abc", allow_agent_send=True)
        self.assertIsNotNone(claimed)
        self.assertEqual(claimed["id"], action_id)
        self.assertIsNone(db.claim_action(self.path, "abc", allow_agent_send=False))
        self.assertTrue(db.complete_action(self.path, action_id, "completed", response="hi"))
        row = db.get_action(self.path, action_id)
        self.assertEqual(row["status"], "completed")
        self.assertEqual(row["response"], "hi")

    def test_rejects_bad_snapshot(self):
        with self.assertRaises(ValueError):
            db.save_snapshot(self.path, {"conversation_id": "abc", "messages": "nope"})
        with self.assertRaises(ValueError):
            db.save_snapshot(self.path, {"conversation_id": "", "messages": []})

    # ---- v2 multi-provider ----

    def test_v1_to_v2_migration_preserves_data(self):
        # setUp already ran init_db (v2 shape); remove it so we can start from a pure v1 database.
        for suffix in ("", "-wal", "-shm"):
            stale = Path(str(self.path) + suffix)
            if stale.exists():
                stale.unlink()
        make_v1_database(self.path)
        db.init_db(self.path)  # runs the migration
        self.assertEqual(db.conversation_count(self.path), 1)
        conversation = db.find_conversation(self.path, "v1-conv")
        self.assertEqual(conversation["provider"], "chatgpt")
        self.assertEqual(conversation["title"], "V1 Title")
        read = db.read_conversation(self.path, "v1-conv")
        self.assertEqual(read["stored_message_count"], 2)
        self.assertEqual(read["messages"][0]["content"], "legacy user text")
        # Idempotent: a second init must not duplicate or break anything.
        db.init_db(self.path)
        self.assertEqual(db.conversation_count(self.path), 1)
        self.assertEqual(db.read_conversation(self.path, "v1-conv")["stored_message_count"], 2)

    def test_same_id_across_providers_is_isolated(self):
        db.save_snapshot(self.path, {"provider": "chatgpt", "conversation_id": "same", "messages": [
            {"key": "m1", "role": "user", "content": "gpt message"}]})
        db.save_snapshot(self.path, {"provider": "claude", "conversation_id": "same", "messages": [
            {"key": "m1", "role": "user", "content": "claude message"}]})
        self.assertEqual(db.conversation_count(self.path), 2)
        self.assertEqual(db.conversation_count(self.path, "claude"), 1)
        chatgpt = db.read_conversation(self.path, "same", provider="chatgpt")
        claude = db.read_conversation(self.path, "same", provider="claude")
        self.assertEqual(chatgpt["messages"][0]["content"], "gpt message")
        self.assertEqual(claude["messages"][0]["content"], "claude message")
        # Unqualified lookup returns the most recently updated conversation.
        self.assertIn(db.find_conversation(self.path, "same")["provider"], ("chatgpt", "claude"))

    def test_provider_stats(self):
        db.save_snapshot(self.path, {"provider": "gemini", "conversation_id": "g1", "messages": [
            {"key": "m1", "role": "assistant", "content": "hi"}]})
        db.save_snapshot(self.path, {"provider": "grok", "conversation_id": "r1", "messages": [
            {"key": "m1", "role": "user", "content": "hey"},
            {"key": "m2", "role": "assistant", "content": "hello"}]})
        stats = db.provider_stats(self.path)
        self.assertEqual(set(stats), {"gemini", "grok"})
        self.assertEqual(stats["gemini"]["messages"], 1)
        self.assertEqual(stats["grok"]["messages"], 2)
        self.assertEqual(stats["gemini"]["label"], "Gemini")

    def test_action_claims_are_provider_scoped(self):
        db.save_snapshot(self.path, {"provider": "claude", "conversation_id": "c1", "messages": [
            {"key": "m1", "role": "user", "content": "x"}]})
        db.save_snapshot(self.path, {"provider": "chatgpt", "conversation_id": "c1", "messages": [
            {"key": "m1", "role": "user", "content": "x"}]})
        action_id = db.queue_action(self.path, "c1", "go", 30, provider="claude")
        claimed = db.claim_action(self.path, "c1", True, provider="claude")
        self.assertEqual(claimed["id"], action_id)
        # The chatgpt twin conversation has no pending action.
        self.assertIsNone(db.claim_action(self.path, "c1", True, provider="chatgpt"))

    def test_unknown_provider_normalizes_to_chatgpt(self):
        db.save_snapshot(self.path, {"provider": "MysteryCorp", "conversation_id": "z", "messages": [
            {"key": "m1", "role": "user", "content": "x"}]})
        self.assertEqual(db.find_conversation(self.path, "z")["provider"], "chatgpt")


if __name__ == "__main__":
    unittest.main(verbosity=2)
