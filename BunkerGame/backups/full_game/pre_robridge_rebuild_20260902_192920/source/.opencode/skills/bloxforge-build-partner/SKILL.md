---
name: bloxforge-build-partner
description: Collaborative creative production pipeline for substantial visual builds. Splits roles across Qwen (reasoning + references), Roblox Assistant (creative builder), BloxForge (engineering), and Muse (art direction). Use when creating or visually modifying environments, props, terrain, structures, or any substantial Roblox content.
---

# BloxForge Build Partner

This skill orchestrates the One-Thing-at-a-time production pipeline via the **Assistant Local Relay** → **Authenticated Bridge** → **BloxForge Worker v1** → **BloxForge MCP** → **Roblox Studio**.

## Security Model

- The authenticated bridge `http://127.0.0.1:62412` **requires a secret token** stored locally at `tools/assistant_bloxforge_bridge/token.txt`.
- **Assistant must never receive the secret.** Do not ask for it, log it, or embed it in prompts, skills, Instances, or scripts.
- The **Assistant Local Relay** (`http://127.0.0.1:62413`) is a localhost-only proxy that injects the credential internally. Assistant communicates **only** with the relay, never with `:62412` directly.

## Relay Endpoint (No Credential Required)

```
ASSISTANT_RELAY_URL = http://127.0.0.1:62413
```

Exposed endpoints (relay binds **only** `127.0.0.1`, never `0.0.0.0`):

- `POST http://127.0.0.1:62413/task`
- `GET  http://127.0.0.1:62413/status/<request_id>`
- `GET  http://127.0.0.1:62413/health`

Do **not** attempt to reach `http://127.0.0.1:62412` directly from Assistant — it will return `401 Unauthorized` without the relay.

## Request Contract (Worker v1 — Read-Only)

Worker v1 supports **only** explicit BloxForge tool calls via `bloxforge.tool`. Natural-language intent is not inferred in v1.

```json
{
  "request_id": "unique-id-123",
  "intent": "bloxforge_tool_call",
  "details": "Human-readable description",
  "studio_context": {
    "project": "BunkerGame"
  },
  "bloxforge": {
    "tool": "get_scene_summary",
    "arguments": {
      "instancePath": "game.Workspace",
      "instance_id": "place:129695090105158"
    }
  }
}
```

### Read-Only Allowlist (v1)

Only these tools are permitted; others return `BLOXFORGE_TOOL_NOT_ALLOWED_V1` **without** any `tools/call` execution:

- `get_connected_instances`
- `get_scene_summary`
- `get_session_summary`
- `get_transport_diagnostics`
- `tool_catalog_search`

If `bloxforge.tool` is absent → fail `MISSING_BLOXFORGE_TOOL`. If `arguments` absent → use `{}`.

Mutation tools such as `execute_luau` are **intentionally blocked** in v1.

## Typical Assistant Flow (via Relay, No Secret)

1. **POST** to `http://127.0.0.1:62413/task` with the JSON above (use `HttpService` or `studio_execute_luau` with `HttpService:RequestAsync`).
2. **Poll** `GET http://127.0.0.1:62413/status/<request_id>` until `status` is `completed` or `failed`.
3. On `completed`, read `result` — this is the **actual parsed BloxForge MCP result** (e.g., `content[0].text` contains JSON string with Studio data).
4. On `failed`, read `error.code` (e.g., `BLOXFORGE_TOOL_NOT_ALLOWED_V1`, `MALFORMED_REQUEST_JSON`).

The relay internally does:

```
Assistant (no credential) -> 127.0.0.1:62413 POST /task
   -> relay reads token from token.txt locally
   -> relay injects X-Bridge-Token header
   -> 127.0.0.1:62412 POST /task (authenticated)
   -> Worker v1 -> 127.0.0.1:58741/mcp tools/call
   -> BloxForge -> Studio
   -> responses/<id>.json -> GET /status/<id>
```

## Health Check

```bash
curl -s http://127.0.0.1:62413/health
# -> {"ok":true,"service":"assistant_relay",...} 200 OK, no credential needed
```

## Example: Read-Only Handshake (via Relay)

```lua
local HttpService = game:GetService("HttpService")
local relay = "http://127.0.0.1:62413"
local id = "assistant-test-"..tostring(math.random(100000,999999))
local body = HttpService:JSONEncode({
  request_id = id,
  intent = "bloxforge_tool_call",
  details = "List connected Studio instances",
  studio_context = {project="BunkerGame"},
  bloxforge = {tool="get_connected_instances", arguments={}}
})
local resp = HttpService:RequestAsync({
  Url = relay.."/task",
  Method = "POST",
  Headers = {["Content-Type"]="application/json"},
  Body = body
})
print(resp.Body)
-- Poll:
-- HttpService:RequestAsync({Url=relay.."/status/"..id, Method="GET"})
```

## What Not To Do

- Do not put the bridge token in any prompt, skill, Instance, attribute, or script.
- Do not print or return the token.
- Do not disable authentication on `:62412`.
- Do not bind the relay to `0.0.0.0`.
- Do not proxy to arbitrary hosts — relay only proxies to `127.0.0.1:62412`.
- Do not add shell or filesystem browsing endpoints.

## Verification

After `POST /task`, `GET /status/<id>` must traverse the real chain `relay -> :62412 -> Worker -> :58741/mcp -> Studio` and return **real Studio data**, not a fake file. Preserve `request_id` as evidence.

