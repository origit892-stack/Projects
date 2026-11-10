import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from db import (claim_action, complete_action, init_db, list_conversations,
                queue_action, read_conversation, save_snapshot, search_messages)


class ChatBridgeDbTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "test.sqlite3"
        init_db(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def test_snapshot_list_search_read(self):
        result = save_snapshot(self.db, {
            "conversation_id": "chat-123", "title": "Roblox economy", "url": "https://chatgpt.com/c/chat-123",
            "messages": [
                {"key": "m1", "role": "user", "content": "Design the pet economy", "ordinal": 0},
                {"key": "m2", "role": "assistant", "content": "Use rebirth-scaled prices", "ordinal": 1},
            ]
        })
        self.assertEqual(result["stored_message_count"], 2)
        self.assertEqual(list_conversations(self.db)[0]["title"], "Roblox economy")
        self.assertEqual(search_messages(self.db, "rebirth")[0]["role"], "assistant")
        conversation = read_conversation(self.db, "chat-123")
        self.assertEqual([m["role"] for m in conversation["messages"]], ["user", "assistant"])

    def test_agent_send_action_lifecycle(self):
        save_snapshot(self.db, {"conversation_id": "chat-456", "title": "Test", "messages": []})
        action_id = queue_action(self.db, "chat-456", "Hello from my agent", 30)
        self.assertIsNone(claim_action(self.db, "chat-456", False))
        claimed = claim_action(self.db, "chat-456", True)
        self.assertEqual(claimed["id"], action_id)
        self.assertTrue(complete_action(self.db, action_id, "completed", response="Hi agent"))
        self.assertEqual(read_conversation(self.db, "chat-456")["stored_message_count"], 0)


if __name__ == "__main__":
    unittest.main()
