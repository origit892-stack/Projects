// Chat Bridge v2 — shared transport. Runs in the isolated world on every supported
// provider page, alongside one adapter per provider (adapter-*.js).
// Adapters register via __cb.registerAdapter(); everything generic lives here.
(() => {
  "use strict";
  if (window.__cbTransport) return;

  const API = "http://127.0.0.1:8765";
  const SNAPSHOT_DEBOUNCE_MS = 900;
  const POLL_MS = 1600;
  const RESYNC_MS = 15000;
  const TICK_MS = 900;
  const VERSION = "2.0.0";

  const registry = new Map();   // provider id -> adapter
  const state = new Map();      // provider id -> runtime state
  window.__cbTransport = true;
  window.__cbInstalled = true;

  function st(provider) {
    if (!state.has(provider)) {
      state.set(provider, { captureTimer: null, lastKey: "", pollBusy: false, busy: false, diagSig: "" });
    }
    return state.get(provider);
  }

  function activeAdapter() {
    for (const adapter of registry.values()) {
      if (adapter.domains.includes(location.hostname)) return adapter;
    }
    return null;
  }

  window.__cb = {
    version: VERSION,
    registerAdapter(adapter) {
      if (adapter && adapter.id && Array.isArray(adapter.domains)) registry.set(adapter.id, adapter);
    },
    _registry: registry
  };

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

  function cleanText(node) {
    return (node ? node.innerText || node.textContent || "" : "").trim();
  }

  function fallbackKeyStore() {
    if (!window.__cb._fallbackKeys) window.__cb._fallbackKeys = { map: new WeakMap(), counter: 0 };
    return window.__cb._fallbackKeys;
  }

  function buildSnapshot(adapter) {
    const conversationId = adapter.conversationId(location);
    if (!conversationId) return null;
    const units = adapter.extractUnits(document);
    const messages = [];
    const fallbacks = fallbackKeyStore();
    units.forEach((unit, index) => {
      const content = (adapter.cleanText ? adapter.cleanText(unit.node) : cleanText(unit.node)).slice(0, 60000);
      if (!content) return;
      let key = unit.key;
      if (!key && !fallbacks.map.has(unit.node)) {
        fallbacks.counter += 1;
        key = `node:${Date.now()}:${fallbacks.counter}`;
        fallbacks.map.set(unit.node, key);
      }
      messages.push({ key, role: unit.role, content, ordinal: index });
    });
    if (!messages.length) return null;
    return {
      version: VERSION,
      provider: adapter.id,
      conversation_id: conversationId,
      title: (document.title || `${adapter.label} conversation`).slice(0, 300),
      url: location.href,
      messages
    };
  }

  function reportDiag(adapter) {
    const conversationId = adapter.conversationId(location);
    if (!adapter.diagnose) return;
    let raw;
    let reasonPrefix = "";
    if (!conversationId) {
      // Not a conversation page (or the URL shape is unknown) — report once per
      // path so a URL-shape miss is visible instead of silent.
      raw = { capture_failed: true, reason: `no conversation id in URL (path: ${location.pathname})`, candidates: {} };
      reasonPrefix = "noid:" + location.pathname;
    } else {
      raw = adapter.diagnose(document);
    }
    const payload = {
      version: VERSION,
      provider: adapter.id,
      conversation_id: conversationId || "",
      url: location.href,
      ts: new Date().toISOString(),
      capture_failed: !!raw.capture_failed,
      reason: raw.reason || "",
      candidates: raw.candidates || {}
    };
    const sig = reasonPrefix + JSON.stringify([payload.capture_failed, payload.reason, payload.candidates]);
    const s = st(adapter.id);
    if (s.diagSig === sig) return;
    s.diagSig = sig;
    try {
      chrome.runtime.sendMessage({ type: "CHAT_BRIDGE_DIAGNOSTIC", diagnostic: payload },
        () => void chrome.runtime.lastError);
    } catch (_) { /* SW asleep; the snapshot path still works */ }
  }

  function snapshotNow(adapter) {
    const snap = buildSnapshot(adapter);
    if (!snap) return;
    const s = st(adapter.id);
    const fingerprint = JSON.stringify([snap.provider, snap.conversation_id, snap.messages.length,
      snap.messages[snap.messages.length - 1]?.key, snap.messages[snap.messages.length - 1]?.content?.slice(-200)]);
    if (fingerprint === s.lastKey) return;
    s.lastKey = fingerprint;
    try {
      chrome.runtime.sendMessage({ type: "CHAT_BRIDGE_SNAPSHOT", snapshot: snap },
        () => void chrome.runtime.lastError);
    } catch (_) { /* ignore */ }
  }

  function scheduleSnapshot(adapter) {
    const s = st(adapter.id);
    clearTimeout(s.captureTimer);
    s.captureTimer = setTimeout(() => snapshotNow(adapter), SNAPSHOT_DEBOUNCE_MS);
  }

  // ---- Agent send (generic; provider hooks come from the adapter) ----

  function findComposerGeneric(adapter) {
    return adapter.findComposer(document);
  }

  async function insertTextGeneric(composer, text) {
    const existingDraft = (composer.value ?? composer.innerText ?? composer.textContent ?? "").trim();
    if (existingDraft) {
      throw new Error("The message box already contains an unsent draft. Clear or send that draft before the agent can send a message.");
    }
    composer.focus && composer.focus();
    if (composer instanceof HTMLTextAreaElement || composer instanceof HTMLInputElement) {
      const setter = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(composer), "value")?.set;
      if (setter) setter.call(composer, text); else composer.value = text;
      composer.dispatchEvent(new Event("input", { bubbles: true }));
    } else {
      document.execCommand && document.execCommand("insertText", false, text);
      if (!cleanText(composer)) {
        composer.textContent = text;
        composer.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: text }));
      }
    }
    await sleep(250);
  }

  async function executeAgentMessage(adapter, action) {
    const conversationId = adapter.conversationId(location);
    const s = st(adapter.id);
    if (s.busy) throw new Error("Another agent message is still in progress on this tab.");
    if (!conversationId || conversationId !== action.conversation_id) {
      throw new Error(`The requested conversation is not the active ${adapter.label} tab. Open that conversation and try again.`);
    }
    const composer = findComposerGeneric(adapter);
    if (!composer) throw new Error(`Could not find the ${adapter.label} message box. The site layout may have changed.`);
    if (cleanText(composer)) {
      throw new Error("The message box already contains an unsent draft. Clear it and ask again.");
    }

    const assistantsBefore = adapter.extractUnits(document).filter((u) => u.role === "assistant");
    const oldLastAssistant = assistantsBefore[assistantsBefore.length - 1] || null;
    const oldText = oldLastAssistant
      ? (adapter.cleanText ? adapter.cleanText(oldLastAssistant.node) : cleanText(oldLastAssistant.node))
      : "";

    s.busy = true;
    try {
      await insertTextGeneric(composer, action.message);

      const sendButton = adapter.findSendButton ? adapter.findSendButton(document, composer) : null;
      if (sendButton) {
        if (sendButton.disabled) throw new Error(`The ${adapter.label} send button is disabled.`);
        sendButton.click();
      } else if (adapter.submitFallback) {
        adapter.submitFallback(composer);
      } else {
        throw new Error(`Could not find a working ${adapter.label} send control. The site layout may have changed.`);
      }
      scheduleSnapshot(adapter);

      const timeoutMs = Math.min(Math.max(action.timeout_ms || 90000, 15000), 120000);
      const deadline = Date.now() + timeoutMs;
      let stableText = "";
      let stableCount = 0;
      const textOf = (node) => (adapter.cleanText ? adapter.cleanText(node) : cleanText(node));
      while (Date.now() < deadline) {
        await sleep(TICK_MS);
        const units = adapter.extractUnits(document);
        const assistants = units.filter((u) => u.role === "assistant");
        const last = assistants[assistants.length - 1] || null;
        const text = last ? textOf(last.node) : "";
        const generating = adapter.isGenerating ? adapter.isGenerating(document) : false;
        const changed = !!text && (last !== oldLastAssistant || text !== oldText);
        if (changed && !generating && text === stableText) stableCount += 1;
        else stableCount = 0;
        stableText = text;
        if (changed && !generating && stableCount >= 2) {
          scheduleSnapshot(adapter);
          return text.slice(0, 60000);
        }
      }
      const assistants = adapter.extractUnits(document).filter((u) => u.role === "assistant");
      const latestNode = assistants[assistants.length - 1];
      const latest = latestNode ? textOf(latestNode.node) : "";
      if (latest && (latest !== oldText || latestNode !== oldLastAssistant)) return latest.slice(0, 60000);
      throw new Error(`Timed out waiting for ${adapter.label} to finish its response. The message may have been sent; check the open tab.`);
    } finally {
      s.busy = false;
    }
  }

  // ---- Per-provider polling ----

  // Shared by the poll loop and the SW push (CHAT_BRIDGE_ACTION). executeAgentMessage
  // is guarded by s.busy, so a double-delivery can never double-send.
  async function handleAction(adapter, action) {
    try {
      const answer = await executeAgentMessage(adapter, action);
      await chrome.runtime.sendMessage({ type: "CHAT_BRIDGE_ACTION_RESULT", result: {
        action_id: action.id, status: "completed", response: answer
      } });
    } catch (error) {
      await chrome.runtime.sendMessage({ type: "CHAT_BRIDGE_ACTION_RESULT", result: {
        action_id: action.id, status: "failed", error: String(error?.message || error)
      } });
    }
  }

  async function poll(provider) {
    const adapter = registry.get(provider);
    const s = st(provider);
    if (!adapter || s.pollBusy) return;
    const conversationId = adapter.conversationId(location);
    if (!conversationId) return;
    s.pollBusy = true;
    try {
      const response = await chrome.runtime.sendMessage({
        type: "CHAT_BRIDGE_POLL", provider, conversation_id: conversationId
      });
      if (response?.ok && response.action) {
        await handleAction(adapter, response.action);
      }
    } catch (_) {
      // Daemon may be stopped; keep the content script alive and retry.
    } finally {
      s.pollBusy = false;
    }
  }

  // ---- Boot ----

  const adapter = activeAdapter();
  if (adapter) {
    window.__cbActiveProvider = adapter.id;
    const observer = new MutationObserver(() => scheduleSnapshot(adapter));
    observer.observe(document.documentElement, { childList: true, subtree: true, characterData: true });
    snapshotNow(adapter);
    reportDiag(adapter);

    // SW push path: the service worker claims actions proactively (immune to
    // background-tab timer throttling) and forwards them here. Message
    // delivery is immediate even in background tabs, so the tab does not have
    // to be in the foreground.
    chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
      if (message?.type !== "CHAT_BRIDGE_ACTION") return false;
      const conversationId = adapter.conversationId(location);
      if (message.provider !== adapter.id || !conversationId ||
          message.action?.conversation_id !== conversationId) {
        sendResponse({ ok: false, error: "Not the tab for this conversation." });
        return false;
      }
      handleAction(adapter, message.action)
        .then(() => sendResponse({ ok: true }))
        .catch((error) => sendResponse({ ok: false, error: String(error?.message || error) }));
      return true;
    });

    setInterval(() => {
      const s = st(adapter.id);
      if (adapter.conversationId(location)) {
        if (!s.captureTimer) scheduleSnapshot(adapter);
        reportDiag(adapter);
      }
      poll(adapter.id);
    }, POLL_MS);
    setInterval(() => {
      if (adapter.conversationId(location)) scheduleSnapshot(adapter);
    }, RESYNC_MS);
  }
})();
