# Chat Bridge 0.1 — local Chrome extension + MCP server

Chat Bridge links the **currently open ChatGPT web conversation** to local AI agents such as Hermes and OpenCode.
It stores captured text in a local SQLite database and exposes MCP tools for listing, searching, reading and (with permission) sending messages in the matching open ChatGPT tab.

## What this MVP does

- Captures user and assistant text rendered in the open `chatgpt.com` conversation.
- Saves data to `~/.chat-bridge/chat-bridge.sqlite3` on this computer.
- Exposes `chatbridge_status`, `chatbridge_list_conversations`, `chatbridge_search_messages`, `chatbridge_read_conversation` and `chatbridge_send_message` over MCP stdio.
- Can send a message only when the matching conversation is open in ChatGPT **and** the extension's **Allow Agent to send messages** switch is enabled.
- Works with multiple local MCP clients: Hermes and OpenCode each start their own lightweight stdio MCP process and use the same SQLite archive.

## Important MVP limits

- This is browser-UI automation, not an official ChatGPT API integration. It reads visible DOM text and uses the visible composer/send button. A ChatGPT UI change can require selector updates.
- Only messages currently rendered in the page are captured. Open the conversation and scroll upward to load older messages if you need them archived. The archive may therefore be partial.
- Text only: file attachments, images, audio, hidden tool payloads and other non-text content are not exported.
- Sending works only in an already-open matching conversation. It does not navigate tabs or create a new ChatGPT conversation.
- Do not run multiple send requests simultaneously to the same tab in this MVP.
- The database is local and not encrypted by this application. Use normal macOS account/file protections and do not share the token.

## Install on macOS

1. Unzip the project folder somewhere stable, for example `~/Projects/chat-bridge`.
2. Open Terminal and run:

   ```bash
   cd ~/Projects/chat-bridge
   ./install_mac.sh
   ```

   The script creates `~/.chat-bridge/`, a Python virtual environment, a random local token and the SQLite file location. Copy the printed token.

3. Open Chrome at `chrome://extensions`, turn on **Developer mode**, click **Load unpacked**, and choose the project's `extension/` folder.
4. Click the Chat Bridge toolbar icon → **Settings**, paste the token and save.
5. Double-click `start.command` in the project folder. Keep its Terminal window open while capturing or sending messages.
6. Open or reload a ChatGPT conversation. The popup should show **Local bridge connected** and its title/ID.

## Connect Hermes

Merge the block in `configs/hermes.example.yaml` into the existing `mcp_servers:` section in `~/.hermes/config.yaml`. Replace the command path with the absolute path to this project's `run_mcp.command`.

Example (adjust the path):

```yaml
mcp_servers:
  chat-bridge:
    command: "/Users/YOUR_USER/Projects/chat-bridge/run_mcp.command"
    args: []
    enabled: true
    timeout: 150
    connect_timeout: 30
```

If `mcp_servers:` already exists, add only the `chat-bridge:` child under it. Do not create a second top-level `mcp_servers:` key. Restart Hermes after saving.

## Connect OpenCode

Merge the `chat-bridge` entry from `configs/opencode.example.jsonc` into the existing `mcp` object in your OpenCode configuration. Replace the command path with the absolute path to `run_mcp.command`.

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "chat-bridge": {
      "type": "local",
      "command": ["/Users/YOUR_USER/Projects/chat-bridge/run_mcp.command"],
      "enabled": true,
      "timeout": 150000
    }
  }
}
```

If your config already contains an `mcp` object, add only the named child. Restart/reload OpenCode and verify that the Chat Bridge tools appear.

## Suggested agent workflow

1. Call `chatbridge_list_conversations` to identify the target conversation.
2. Call `chatbridge_read_conversation` with its ID to read its archived context.
3. Use `chatbridge_search_messages` to locate older decisions across chats.
4. To talk to ChatGPT, keep the matching conversation open in Chrome, enable **Allow Agent to send messages** in the extension popup, then call `chatbridge_send_message` with the conversation ID and message.

## Local tests

From the project folder:

```bash
python3 -m unittest discover -s host/tests -v
python3 -m py_compile host/db.py host/bridge_daemon.py host/mcp_server.py
```

## Security model

- The local HTTP service binds only to `127.0.0.1:8765`.
- Browser requests require a random token and a `chrome-extension://` origin.
- The extension's permission scope is limited to ChatGPT domains and the local loopback bridge.
- MCP access is local stdio: there is no public endpoint and no cloud sync.
- Agent sending is off by default and must be enabled in the extension popup.
