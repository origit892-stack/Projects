#!/usr/bin/env python3
"""The Agent Operator — Telegram intake bot (v1).
Long-poll, stdlib only. Auto-greeting + intake, logs every message to INBOX.jsonl.
Token: ~/.hermes/freelance-income/telegram_bot.token (chmod 600, NOT in git).
The operator (user) replies to leads by telling the chief in chat; the chief sends via the Bot API.
"""
import json, os, time, urllib.request, urllib.parse, datetime

TOKEN = None
HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.expanduser("~/.hermes/freelance-income/telegram_bot.token")
INBOX = os.path.join(HERE, "INBOX.jsonl")
SITE = "https://origit892-stack.github.io/agent-operator/"

GREETING = (
    "Hi! You reached <b>The Agent Operator</b> — I build AI employees and automations "
    "that run 24/7. Fixed price: $300 / $900 / $2,000+.\n\n"
    "To point you to the right package, three quick things:\n"
    "1. What task do you want automated?\n"
    "2. Which tools are involved (email, CRM, sheets, WhatsApp, ...)?\n"
    "3. Rough budget: $300 / $900 / $2,000+?\n\n"
    "More: " + SITE
)
FOLLOWUP = "Got it — the operator reads everything and replies personally, usually within a few hours."

def api(method, **params):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(url, data=data, timeout=70) as r:
        return json.loads(r.read())

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def log(rec):
    with open(INBOX, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def handle(msg):
    chat = msg.get("chat") or {}
    chat_id = chat.get("id")
    text = (msg.get("text") or "").strip()
    user = msg.get("from") or {}
    log({"type": "message", "at": now(), "chat_id": chat_id,
         "user": {"id": user.get("id"),
                  "name": f'{user.get("first_name", "")} {user.get("last_name", "")}'.strip(),
                  "username": user.get("username")},
         "text": text})
    if not chat_id:
        return
    reply = GREETING if text.lower() in ("/start", "hi", "hello", "hey") or len(text) < 12 else FOLLOWUP
    api("sendMessage", chat_id=chat_id, text=reply, parse_mode="HTML")

def main():
    global TOKEN
    with open(TOKEN_FILE) as f:
        TOKEN = f.read().strip()
    log({"type": "bot_start", "at": now()})
    offset = 0
    while True:
        try:
            res = api("getUpdates", offset=offset, timeout=50, allowed_updates="message")
            for u in res.get("result", []):
                offset = u["update_id"] + 1
                msg = u.get("message") or u.get("edited_message")
                if msg:
                    handle(msg)
        except Exception as e:
            log({"type": "error", "at": now(), "error": str(e)[:200]})
            time.sleep(15)

if __name__ == "__main__":
    main()
