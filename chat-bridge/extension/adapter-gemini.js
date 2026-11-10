// Chat Bridge v2 — Gemini adapter (gemini.google.com).
// BEST-EFFORT: selectors are candidates, not verified. Diagnostics are the
// contract: if capture fails the popup/MCP surfaces a reason, and this file
// is updated in the repo after visual verification.
(() => {
  "use strict";

  function conversationId(loc) {
    // gemini.google.com/app/<id> and /app/u/0/<id>
    const match = loc.pathname.match(/\/app\/(?:u\/\d+\/)?([^/?#]+)/);
    return match ? match[1] : null;
  }

  function cleanText(node) {
    return (node.innerText || node.textContent || "").trim();
  }

  function extractUnits(doc) {
    const units = [];
    const seen = new Set();
    // Candidate 1: model/user message containers.
    doc.querySelectorAll('model-response, model-turn, user-query').forEach((el) => {
      if (seen.has(el)) return;
      seen.add(el);
      const role = el.tagName === "USER-QUERY" ? "user" : "assistant";
      const id = el.getAttribute("message-id") || el.id || "";
      units.push({ node: el, role, key: id ? `dom:${id}` : `${role}:${units.length}` });
    });
    // Candidate 2: message classes.
    if (!units.length) {
      doc.querySelectorAll('[class*="response-container"], [class*="query-container"], [data-message-id]').forEach((el) => {
        if (seen.has(el)) return;
        seen.add(el);
        const cls = el.className || "";
        const role = /query|user|prompt/i.test(cls + (el.getAttribute("data-message-role") || "")) ? "user" : "assistant";
        const id = el.getAttribute("data-message-id") || "";
        units.push({ node: el, role, key: id ? `dom:${id}` : `${role}:${units.length}` });
      });
    }
    return units;
  }

  function findComposer(doc) {
    return doc.querySelector('rich-textarea [contenteditable="true"]')
      || doc.querySelector('textarea[aria-label*="Gemini" i]')
      || doc.querySelector('[data-id="prompt-container"] [contenteditable="true"]')
      || [...doc.querySelectorAll('[contenteditable="true"]')]
        .filter((el) => el.getBoundingClientRect().height > 0).pop()
      || null;
  }

  function findSendButton(doc, composer) {
    return doc.querySelector('button[aria-label*="Send" i]')
      || doc.querySelector('[data-id="send-button"]')
      || [...doc.querySelectorAll('button')].find((b) =>
        /send message|send|שלח/i.test(b.getAttribute("aria-label") || b.title || ""))
      || null;
  }

  // Gemini sends on Enter (shift+enter = newline).
  function submitFallback(composer) {
    composer.dispatchEvent(new KeyboardEvent("keydown", {
      key: "Enter", code: "Enter", keyCode: 13, which: 13, bubbles: true, cancelable: true
    }));
  }

  function isGenerating(doc) {
    return !!doc.querySelector('button[aria-label*="Stop" i], [data-id="stop-button"], model-response[is-loading="true"]');
  }

  function diagnose(doc) {
    const candidates = {
      model_tags: doc.querySelectorAll('model-response, model-turn, user-query').length,
      response_container: doc.querySelectorAll('[class*="response-container"], [class*="query-container"]').length,
      data_message_id: doc.querySelectorAll('[data-message-id]').length,
      editables: doc.querySelectorAll('[contenteditable="true"]').length,
      composer: !!findComposer(doc)
    };
    const found = candidates.model_tags + candidates.response_container + candidates.data_message_id;
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
    id: "gemini",
    label: "Gemini",
    domains: ["gemini.google.com"],
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
