# Chat Bridge v2 — Multi-Provider Spec (Claude, Gemini, ChatGPT, Grok)

Status: SPEC (implementation contract). Version target: manifest 2.0.0.
Working tree for v2: THIS repo copy (`chat-bridge/`). Do NOT touch the live operational copy at `~/Downloads/chat-bridge` and do NOT touch port 8765 — the v1 daemon keeps running there.

## 1. Goal
Generalize v1 (ChatGPT-only) into a multi-provider bridge for the user's OPEN web conversations on:
- ChatGPT — chatgpt.com, chat.openai.com  (selectors VERIFIED 2026-11-10, high confidence)
- Claude — claude.ai  (best-effort selectors, drift-prone → diagnostics REQUIRED)
- Gemini — gemini.google.com  (best-effort, diagnostics REQUIRED)
- Grok — grok.com  (lowest confidence, diagnostics REQUIRED)

Requirements:
1. Per-provider DOM adapters, one transport layer (shared.js).
2. Unified SQLite storage with a `provider` column (v1 data migrated as `provider='chatgpt'`).
3. MCP tools gain an optional `provider` param; new `chatbridge_provider_status` tool.
4. Daemon `/healthz`; popup polls it with retry and shows a proper "Daemon offline" state (this subsumes the known v1 bug "Bridge unavailable: Failed to fetch" — in v2 the popup must degrade gracefully, never show a raw fetch error).
5. The verified ChatGPT capture+send path MUST keep working byte-for-byte behaviorally (same message keys → same upsert semantics).

## 2. File layout (extension/)
```
manifest.json          # v2.0.0; content_scripts over all provider domains, js list:
                       #   shared.js, adapter-chatgpt.js, adapter-claude.js,
                       #   adapter-gemini.js, adapter-grok.js  (shared FIRST)
shared.js              # NEW — transport + adapter registry + snapshot loop + agent-action handling
adapter-chatgpt.js     # NEW — v1 logic moved/rewritten per adapter contract (verified selectors)
adapter-claude.js      # NEW
adapter-gemini.js      # NEW
adapter-grok.js        # NEW
background.js          # MODIFY — pass provider through; per-provider lastConversation/diagnostics in storage
content.js             # DELETE (replaced by shared.js + adapters)
popup.html / popup.js / popup.css   # MODIFY — v2 status UI (health poll + provider rows)
options.html/js        # unchanged
```

## 3. Adapter contract (all adapters are plain files sharing the isolated-world `window`)
`shared.js` exposes `window.__cb.registerAdapter(adapter)` and the transport. Each adapter file calls it exactly once:
```js
window.__cb.registerAdapter({
  id: 'claude',                     // stable key: chatgpt | claude | gemini | grok
  domains: ['claude.ai'],           // hostname-suffix match (covers www.)
  conversationId: (loc) => string|null,   // from location.pathname
  extract: (doc) => units,          // [{key, role:'user'|'assistant', content, ordinal}]
                                    // key = STABLE per message (uuid attr if present, else sha-ish hash of role+text+index)
                                    // content = clean innerText (strip 'ChatGPT said:'-style prefixes), non-empty only
  findComposer: (doc) => el|null,   // visible contenteditable/textarea
  findSendButton: (doc, composer) => el|null,
  diagnose: (doc) => object         // counts per candidate selector — used when extract() returns 0
});
```
`shared.js` provides the DEFAULTS adapters may skip:
- `insertText(composer, text)`: focus() + `document.execCommand('insertText', false, text)` (works in ProseMirror/CodeMirror/contenteditable); fallback: set `textContent` + input event.
- `detectReply(doc, baselineUnits)`: after send, poll (≤60s, 1.5s steps) for a NEW assistant unit (key not in baseline) → return its content.
Snapshot loop (per open tab, from v1): MutationObserver + 15s interval → debounced 900ms →
`chrome.runtime.sendMessage({type:'CHAT_BRIDGE_SNAPSHOT', snapshot:{provider, conversation_id, title, url, messages}})`
When extract() returns 0 for a provider page that has a conversationId: send `{type:'CHAT_BRIDGE_DIAGNOSTIC', provider, conversation_id, diag: adapter.diagnose(doc)}` (SW stores latest per provider; do NOT spam — max 1 per 60s per provider).

## 4. Selector maps

### ChatGPT (VERIFIED 2026-11-10 — keep exactly; old v1 selectors as second fallback)
- units: `[data-chatgpt-search-unit-key]`; role from key suffix `:user` / `:assistant`
- stable key: first UUID of `data-chatgpt-search-message-ids` (attr is on the unit element), else `'dom:'+key`
- content: innerText, strip `^ChatGPT said:\s*` (case-insensitive)
- composer: `.ProseMirror[role="textbox"]` (visible: offsetHeight>0)
- send: inside the composer's closest footer/toolbar, the primary action button (v1 logic: data-testid → aria-label /send/i → footer primary-action slot)
- legacy fallback selectors (v1 originals): `[data-message-author-role]`, `#prompt-textarea`
- conversationId: pathname `/c/<uuid>`

### Claude (claude.ai — best-effort 2026, MUST diagnose)
- conversationId: pathname `/chat/<uuid>`
- user units candidates (in order): `[data-view="user"] .markdown`, `[data-view="user"]`, `.message[data-message-role="user"]`, `.message.user`
- assistant units candidates: `[data-view="assistant"] .markdown`, `[data-view="assistant"]`, `.message[data-message-role="assistant"]`, `.streaming-message`
- de-dup: if multiple candidates match the same visual message, prefer the most specific; unit key = element uuid attr if present (`data-message-id`, `id`) else hash(role + '|' + content)
- composer candidates: `div.cm-content[contenteditable="true"]`, `div[contenteditable="true"][data-clipboard-cs-language]`, last visible `div[contenteditable="true"]`
- send: button in the composer container's footer with aria-label /send/i or a visible SVG arrow; fallback: submit on Enter keydown dispatch when no button found

### Gemini (gemini.google.com — best-effort 2026, MUST diagnose)
- conversationId: pathname `/app/<id>` (take the path segment after /app; may be `/app/<id>?hl=...`)
- user units candidates: `user-query .query-text`, `div.message-content.user-query .query-text`, `button.user-query-button`
- assistant units candidates: `model-response .markdown`, `div.message-content.model-response .markdown`, `message-content.model-response`
- unit key: hash(role + '|' + content + '|' + index)
- composer candidates: `rich-textarea div.ql-editor[contenteditable="true"]`, `rich-textarea div[contenteditable="true"]`, last visible contenteditable
- send: `button.send-button`, else button with aria-label /send/i near composer; fallback Enter dispatch

### Grok (grok.com — lowest confidence, MUST diagnose)
- conversationId: pathname `/chat/<id>` or first path segment that looks like an id (uuid-like); else null
- units candidates (generic heuristics, in order): `[data-message-id]`, `.message[data-role]` (role attr value user/assistant), `.message.user`, `.message.assistant`
- If none match: diagnose() reports counts of `.message`, `[class*="message"]`, `[data-message-id]`, `.markdown`, and the page title — enough to iterate from
- composer candidates: `div[contenteditable="true"]` (visible, inside bottom region), `textarea[contenteditable]`, last visible textarea/contenteditable
- send: button with aria-label /send/i or class containing `send`; fallback Enter dispatch

Diagnose object shape (all adapters): `{title, unitCounts: {selector: count}, composerCandidates: {selector: count}, sampleTexts: [first 3 short text snippets of candidate elements]}` — text snippets truncated to 80 chars (privacy: local-only storage).

## 5. host/ changes

### db.py — schema v2
- `conversations` gains `provider TEXT NOT NULL DEFAULT 'chatgpt'`; UNIQUE(provider, id)
- Migration on connect: if column missing → `ALTER TABLE conversations ADD COLUMN provider TEXT NOT NULL DEFAULT 'chatgpt'`; recreate/replace any old unique index on id alone with (provider, id). Idempotent.
- `upsert_conversation(provider, id, title, url)`; `upsert_messages(conversation_id, units)` unchanged semantics.
- New: `provider_stats()` → {provider: {conversations, messages, last_updated}}

### bridge_daemon.py
- `PORT` env-overridable (default 8765) — tests use 8766.
- `GET /healthz` → `{ok:true, version:"2.0.0", uptime_s, providers: provider_stats()}` (200). NO token needed for /healthz (local-only, no secrets in it).
- `/capture` and `/next-action`: token+origin auth as in v1; capture body gains `provider` (default 'chatgpt' for back-compat).
- `/next-action` response: per-provider queue behavior — a 'send' action targets the provider+conversation pair; SW polls `/next-action?provider=X` (or body field) and the daemon only dispatches queued actions for that provider. Keep v1 behavior for provider-less polls (chatgpt).

### mcp_server.py — tools (keep v1 names, all new params OPTIONAL)
- `chatbridge_status()` → v1 shape + `providers` map
- `chatbridge_list_conversations(provider?)`
- `chatbridge_read_conversation(conversation_id, provider?)` — provider omitted: auto-detect from stored row
- `chatbridge_search_messages(query, provider?)`
- `chatbridge_send_message(conversation_id, message, provider?)` — same "waits for assistant reply" behavior (SW/next-action loop, timeout ≤150s)
- NEW `chatbridge_provider_status()` → per provider: open tab? last capture ts, last diag (if capture failing) — read from daemon state endpoint `GET /providers` (token-authed) which the daemon fills from SW-pushed diagnostics (SW forwards diagnostics to daemon via a new `POST /diag` endpoint, token-authed)

## 6. background.js (SW) changes
- SNAPSHOT handler: store per-provider `lastConversation` (chrome.storage.local key `lastConversation_<provider>`), forward to daemon `/capture` with provider.
- NEW `CHAT_BRIDGE_DIAGNOSTIC` handler: store `diag_<provider>` (latest, with ts), forward `POST /diag` (fire-and-forget).
- NEXT-ACTION: include `provider` in the poll; execute agent action (send) via the adapter registry in the content script (the content script does composer/send/detectReply; SW just relays).
- Keep the v1 poll cadence (1.6s) and token/origin handling identical.

## 7. popup v2
- Poll `GET /healthz` every 2s (fetch with 3s timeout).
  - OK → "Local bridge connected" + per-provider rows (from `GET /providers` if token set, else from lastConversation_ keys): provider name, last-captured conversation title, elapsed time, red dot + "diagnostics" detail if diag is stale/failing.
  - FAILED (any fetch error) → clear panel: "Daemon offline — run `./start.command` in the project folder" + Retry now button. NO raw "Failed to fetch" text anywhere.
- `Allow Agent to send messages` toggle: same storage key as v1 (back-compat).
- Token entry: same as v1.

## 8. Testing (ALL must pass; run them and paste output into the final summary)
1. `python -m unittest discover -s host/tests -v` — extend tests: schema v2 migration (fresh + upgraded v1 db), provider upserts, provider_stats.
2. `python -m py_compile host/db.py host/bridge_daemon.py host/mcp_server.py`
3. `node --check` on every extension/*.js
4. Node adapter logic tests (`host/tests/node/` — plain node, no npm deps; stub a minimal `document` with `querySelectorAll`/`querySelector` returning fake elements): for each adapter — extract() maps candidate selectors to units with correct roles/keys; conversationId parsing for 2-3 URL shapes each.
5. Daemon smoke on PORT=8766 with a temp DB (env var for db path or --db flag; add if missing): start → `/healthz` 200 → `/capture` (chatgpt: 2 units; claude: 2 units) → `/providers` shows both → `/next-action?provider=claude` returns queued action only for claude → kill. Do NOT start anything on 8765.
6. MCP stdio smoke: initialize + tools/list over the daemon (expect 6 tools).
7. Do NOT modify `~/Downloads/chat-bridge`, do NOT open browsers, do NOT install packages (python: use the existing venv `~/.chat-bridge/venv` by PYTHONPATH; node: system node only).

## 9. Constraints
- Keep the token auth model (random local token + chrome-extension origin check).
- No new runtime dependencies (no npm, no extra pip packages).
- v1 DB must open cleanly in v2 (migration, no data loss).
- All provider keys lowercase; UI labels capitalized.
- Comments in code: English. Repo language: code English, README additions may be EN (keep README_HE as-is or append a short v2 section in HE at the end).
