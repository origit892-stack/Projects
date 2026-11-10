# Chat Bridge 2.0 — local Chrome extension + MCP server (multi-provider)

Chat Bridge links the **currently open web conversations on ChatGPT, Claude, Gemini, and Grok** to local AI agents such as Hermes and OpenCode.
It stores captured text in a local SQLite database and exposes MCP tools for listing, searching, reading and (with permission) sending messages in the matching open provider tab.

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

## v2: multi-provider (2.0.0)

- **Providers:** ChatGPT (`chatgpt.com`, `chat.openai.com`), Claude (`claude.ai`), Gemini (`gemini.google.com`), Grok (`grok.com`).
- **Architecture:** one shared transport (`extension/shared.js`) plus one DOM adapter per provider (`extension/adapter-*.js`). The active adapter is chosen by hostname; each registers extraction, composer/send, and diagnostic hooks.
- **Storage:** the SQLite schema now carries a `provider` column (composite primary keys). An existing v1 database migrates automatically on daemon start, with all legacy rows recorded as `provider='chatgpt'`.
- **Daemon:** new endpoints `GET /healthz` (no token needed), `GET /providers` (stats + latest capture diagnostics), `POST /diag`. Both auth styles work: v2 `Authorization: Bearer <token>` and v1 `X-Chat-Bridge-Token: <token>`.
- **MCP:** every tool accepts an optional `provider` argument (empty = all providers / auto-infer). New tool `chatbridge_provider_status` reports per-provider counts, last capture time, and the latest capture diagnostic.
- **Popup:** shows a proper **Daemon offline** state with start instructions (the old "Failed to fetch" dead end), plus a per-provider status list. If a provider's page layout changes, the adapter reports `capture_failed` with the candidate-selector counts, so the breakage is visible instead of silent.
- **Provider verification status:** the ChatGPT adapter ports the verified 2026-11-10 selectors verbatim. The Claude, Gemini, and Grok adapters are **best-effort candidates** — if one of them reports `capture_failed` in the popup or `chatbridge_provider_status`, update `extension/adapter-<provider>.js` with the selectors found in DevTools and reload the extension.
- **Compatibility:** the v1 extension keeps working against the v2 daemon (same token file, same DB, same message flow). The v2 extension works against a v1 daemon for read/status (sending new providers obviously requires v2).
- **Test port:** test the v2 daemon on port 8766 to avoid disturbing a running v1 bridge: `python3 host/bridge_daemon.py --port 8766 --db /tmp/cb2.sqlite3 --config /tmp/cb2-config.json`.

## Local tests

From the project folder:

```bash
python3 -m unittest discover -s host/tests -v
python3 -m py_compile host/db.py host/bridge_daemon.py host/mcp_server.py
node --check extension/shared.js extension/adapter-chatgpt.js extension/adapter-claude.js extension/adapter-gemini.js extension/adapter-grok.js extension/background.js extension/popup.js extension/options.js
node host/tests/node/adapters.test.js
```

## Security model

- The local HTTP service binds only to `127.0.0.1:8765`.
- Browser requests require a random token and a `chrome-extension://` origin.
- The extension's permission scope is limited to the four provider domains (ChatGPT, Claude, Gemini, Grok) and the local loopback bridge.
- MCP access is local stdio: there is no public endpoint and no cloud sync.
- Agent sending is off by default and must be enabled in the extension popup.
