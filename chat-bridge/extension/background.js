// Chat Bridge v2 — service worker. Provider-aware relay between content
// scripts and the local daemon. v1-compatible: X-Chat-Bridge-Token header,
// same message types, lastConversation stored per provider.
const API = "http://127.0.0.1:8765";
const VERSION = "2.0.0";

async function settings() {
  return await chrome.storage.local.get({
    token: "",
    allowAgentSend: false,
    lastError: ""
  });
}

async function request(path, options = {}) {
  const cfg = await settings();
  if (!cfg.token) throw new Error("Missing local bridge token. Open Chat Bridge settings and paste the token from install.sh.");
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(`${API}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        "X-Chat-Bridge-Token": cfg.token,
        ...(options.headers || {})
      }
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.error || `Local bridge returned HTTP ${response.status}`);
    return body;
  } finally {
    clearTimeout(timer);
  }
}

// Tokenless health probe (v2 daemon's /healthz needs no token) so the popup
// can distinguish "daemon offline" from "daemon online, token wrong".
async function healthz() {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 2500);
  try {
    const response = await fetch(`${API}/healthz`, { signal: controller.signal });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(`Local bridge returned HTTP ${response.status}`);
    return body;
  } finally {
    clearTimeout(timer);
  }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    try {
      if (message?.type === "CHAT_BRIDGE_SNAPSHOT") {
        const snapshot = message.snapshot || {};
        const provider = snapshot.provider || "chatgpt";
        await chrome.storage.local.set({
          [`lastConversation_${provider}`]: {
            id: snapshot.conversation_id,
            title: snapshot.title,
            url: snapshot.url,
            capturedAt: new Date().toISOString()
          },
          lastError: ""
        });
        const result = await request("/capture", { method: "POST", body: JSON.stringify(snapshot) });
        sendResponse({ ok: true, ...result });
      } else if (message?.type === "CHAT_BRIDGE_DIAGNOSTIC") {
        const diag = message.diagnostic || {};
        const provider = diag.provider || "chatgpt";
        await chrome.storage.local.set({ [`chatbridge_diag_${provider}`]: diag });
        try {
          await request("/diag", { method: "POST", body: JSON.stringify(diag) });
        } catch (_) {
          // Diagnostics are best-effort; the local copy in storage remains.
        }
        sendResponse({ ok: true });
      } else if (message?.type === "CHAT_BRIDGE_POLL") {
        const cfg = await settings();
        const provider = message.provider || "chatgpt";
        const result = await request("/next-action", {
          method: "POST",
          body: JSON.stringify({
            provider,
            conversation_id: message.conversation_id,
            allow_agent_send: Boolean(cfg.allowAgentSend)
          })
        });
        sendResponse({ ok: true, action: result.action || null });
      } else if (message?.type === "CHAT_BRIDGE_ACTION_RESULT") {
        const result = await request("/action-result", { method: "POST", body: JSON.stringify(message.result) });
        sendResponse({ ok: true, ...result });
      } else if (message?.type === "CHAT_BRIDGE_HEALTH") {
        try {
          const result = await healthz();
          sendResponse({ ok: true, ...result });
        } catch (healthError) {
          // Fall back to the token-gated /health (works with older daemons).
          const result = await request("/health");
          sendResponse({ ok: true, ...result });
        }
      } else if (message?.type === "CHAT_BRIDGE_PROVIDERS") {
        const health = await healthz().catch(() => null);
        let providers = {};
        try {
          providers = (await request("/providers")).providers || {};
        } catch (_) { /* token missing or daemon offline; storage fallback below */ }
        if (!Object.keys(providers).length) {
          const stored = await chrome.storage.local.get(null);
          for (const provider of ["chatgpt", "claude", "gemini", "grok"]) {
            const diag = stored[`chatbridge_diag_${provider}`];
            if (diag) providers[provider] = { provider, label: provider, capture_failed: !!diag.capture_failed, diag };
          }
        }
        sendResponse({ ok: true, health, providers });
      } else if (message?.type === "CHAT_BRIDGE_ROTATE") {
        const result = await request("/rotate-token", { method: "POST", body: "{}" });
        if (result?.token) {
          await chrome.storage.local.set({ token: result.token });
        }
        sendResponse({ ok: true, ...result });
      } else {
        sendResponse({ ok: false, error: "Unknown Chat Bridge message." });
      }
    } catch (error) {
      await chrome.storage.local.set({ lastError: String(error?.message || error) });
      sendResponse({ ok: false, error: String(error?.message || error) });
    }
  })();
  return true;
});

// Keep the service worker alive so content-script messages are never lost.
chrome.alarms.create("chat-bridge-keepalive", { periodInMinutes: 0.4 });
chrome.alarms.onAlarm.addListener(() => {});
