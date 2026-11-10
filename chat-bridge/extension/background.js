const API = "http://127.0.0.1:8765";

async function settings() {
  return await chrome.storage.local.get({ token: "", allowAgentSend: false, lastConversation: null, lastError: "" });
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

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    try {
      if (message?.type === "CHAT_BRIDGE_SNAPSHOT") {
        const cfg = await settings();
        await chrome.storage.local.set({ lastConversation: {
          id: message.snapshot.conversation_id,
          title: message.snapshot.title,
          url: message.snapshot.url,
          capturedAt: new Date().toISOString()
        }, lastError: "" });
        const result = await request("/capture", { method: "POST", body: JSON.stringify(message.snapshot) });
        sendResponse({ ok: true, ...result });
      } else if (message?.type === "CHAT_BRIDGE_POLL") {
        const cfg = await settings();
        const result = await request("/next-action", {
          method: "POST",
          body: JSON.stringify({
            conversation_id: message.conversation_id,
            allow_agent_send: Boolean(cfg.allowAgentSend)
          })
        });
        sendResponse({ ok: true, action: result.action || null });
      } else if (message?.type === "CHAT_BRIDGE_ACTION_RESULT") {
        const result = await request("/action-result", { method: "POST", body: JSON.stringify(message.result) });
        sendResponse({ ok: true, ...result });
      } else if (message?.type === "CHAT_BRIDGE_HEALTH") {
        const result = await request("/health");
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
