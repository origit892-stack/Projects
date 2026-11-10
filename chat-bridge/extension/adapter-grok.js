// Chat Bridge v2 — Grok adapter (grok.com).
// BEST-EFFORT: selectors are candidates, not verified. Diagnostics are the
// contract: if capture fails the popup/MCP surfaces a reason, and this file
// is updated in the repo after visual verification.
(() => {
  "use strict";

  function conversationId(loc) {
    // grok.com/c/<uuid> (current DOM); /chat/<id> kept as fallback candidate
    const match = loc.pathname.match(/\/c\/([^/?#]+)/) || loc.pathname.match(/\/chat\/([^/?#]+)/);
    return match ? match[1] : null;
  }

  function cleanText(node) {
    return (node.innerText || node.textContent || "").trim();
  }

  function extractUnits(doc) {
    const units = [];
    const seen = new Set();
    // Candidate 1: message list items with role/author markers.
    doc.querySelectorAll('[data-message-role], [data-author-role]').forEach((el) => {
      if (seen.has(el)) return;
      seen.add(el);
      const role = el.getAttribute("data-message-role") || el.getAttribute("data-author-role") || "";
      const mapped = /user|human|you/i.test(role) ? "user" : /assistant|grok|model|ai/i.test(role) ? "assistant" : null;
      const id = el.getAttribute("data-message-id") || el.id || "";
      if (mapped) units.push({ node: el, role: mapped, key: id ? `dom:${id}` : `${mapped}:${units.length}` });
    });
    // Candidate 2: structural turns.
    if (!units.length) {
      doc.querySelectorAll('[class*="message-row"], [class*="chat-message"], [data-turn-id]').forEach((el) => {
        if (seen.has(el)) return;
        seen.add(el);
        const isUser = /user|human|you|prompt/i.test(el.className + (el.getAttribute("data-turn-role") || ""));
        units.push({ node: el, role: isUser ? "user" : "assistant", key: `turn:${units.length}` });
      });
    }
    return units;
  }

  function findComposer(doc) {
    return doc.querySelector('[data-testid="chat-input"] textarea')
      || doc.querySelector('textarea[placeholder*="Grok"]')
      || doc.querySelector('[contenteditable="true"][role="textbox"]')
      || [...doc.querySelectorAll('textarea, [contenteditable="true"]')]
        .filter((el) => el.getBoundingClientRect().height > 0).pop()
      || null;
  }

  function findSendButton(doc, composer) {
    return doc.querySelector('button[data-testid="send-button"]')
      || doc.querySelector('button[aria-label*="Send" i]')
      || [...doc.querySelectorAll('button')].find((b) =>
        /send message|send|שלח/i.test(b.getAttribute("aria-label") || b.title || ""))
      || null;
  }

  // Grok sends on Enter (shift+enter = newline).
  function submitFallback(composer) {
    composer.dispatchEvent(new KeyboardEvent("keydown", {
      key: "Enter", code: "Enter", keyCode: 13, which: 13, bubbles: true, cancelable: true
    }));
  }

  function isGenerating(doc) {
    return !!doc.querySelector('button[aria-label*="Stop" i], [data-testid="stop-button"]');
  }

  function diagnose(doc) {
    const candidates = {
      role_attrs: doc.querySelectorAll('[data-message-role], [data-author-role]').length,
      structural: doc.querySelectorAll('[class*="message-row"], [class*="chat-message"], [data-turn-id]').length,
      editables: doc.querySelectorAll('textarea, [contenteditable="true"]').length,
      composer: !!findComposer(doc)
    };
    const found = candidates.role_attrs + candidates.structural;
    return {
      capture_failed: !found,
      reason: found
        ? ""
        : (candidates.composer
          ? "no message selectors matched; composer present — candidate list needs updating (see candidates)"
          : "no message selectors and no composer — page may be pre-login or a different layout"),
      candidates
    };
  }

  window.__cb.registerAdapter({
    id: "grok",
    label: "Grok",
    domains: ["grok.com"],
    conversationId,
    extractUnits,
    cleanText,
    findComposer,
    findSendButton,
    submitFallback,
    isGenerating,
    diagnose
  });
})();
