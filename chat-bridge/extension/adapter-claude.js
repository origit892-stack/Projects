// Chat Bridge v2 — Claude adapter (claude.ai).
// BEST-EFFORT: selectors are candidates, not verified. Diagnostics are the
// contract: if capture fails the popup/MCP surfaces a reason, and this file
// is updated in the repo after visual verification.
(() => {
  "use strict";

  function conversationId(loc) {
    // claude.ai/chat/<uuid>
    const match = loc.pathname.match(/\/chat\/([^/?#]+)/);
    return match ? match[1] : null;
  }

  function cleanText(node) {
    return (node.innerText || node.textContent || "").trim();
  }

  function extractUnits(doc) {
    const units = [];
    const seen = new Set();
    // Candidate 1: Claude renders user messages with a view attribute.
    doc.querySelectorAll('[data-view="user"], [data-user-message="true"]').forEach((el) => {
      if (seen.has(el)) return;
      seen.add(el);
      units.push({ node: el, role: "user", key: `user:${units.length}` });
    });
    // Candidate 2: Claude assistant blocks (streaming container / markdown blocks).
    doc.querySelectorAll('[data-stream="true"] .markdown, [data-test-id="assistant-message"], [class*="message-container"][data-message-author-role="assistant"]').forEach((el) => {
      if (seen.has(el)) return;
      seen.add(el);
      units.push({ node: el, role: "assistant", key: `assistant:${units.length}` });
    });
    // Candidate 3: structural — top-level turn wrappers in the transcript.
    if (!units.length) {
      doc.querySelectorAll('[data-conversation-turn], [class*="conversation-turn"], [data-testid^="message-"]').forEach((el) => {
        if (seen.has(el)) return;
        seen.add(el);
        const isUser = /(^|\b)(user|human|prompt)(\b|$)/i.test(el.getAttribute("data-conversation-turn") || el.className || "");
        units.push({ node: el, role: isUser ? "user" : "assistant", key: `turn:${units.length}` });
      });
    }
    return units;
  }

  function findComposer(doc) {
    return doc.querySelector('#claude-chat-provider-portal [contenteditable="true"]')
      || doc.querySelector('[data-testid="prompt-textarea"]')
      || doc.querySelector('div[contenteditable="true"][role="textbox"]')
      || [...doc.querySelectorAll('[contenteditable="true"]')]
        .filter((el) => el.getBoundingClientRect().height > 0).pop()
      || null;
  }

  function findSendButton(doc, composer) {
    return doc.querySelector('button[data-testid="send-button"]')
      || [...doc.querySelectorAll('button')].find((b) =>
        /send message|send|שלח/i.test(b.getAttribute("aria-label") || b.title || ""))
      || null;
  }

  // Claude sends on Enter (shift+enter = newline) when no button is found.
  function submitFallback(composer) {
    composer.dispatchEvent(new KeyboardEvent("keydown", {
      key: "Enter", code: "Enter", keyCode: 13, which: 13, bubbles: true, cancelable: true
    }));
  }

  function isGenerating(doc) {
    return !!doc.querySelector('[data-stream="true"], [data-testid="stop-button"], button[aria-label*="Stop"]');
  }

  function diagnose(doc) {
    const candidates = {
      user_view: doc.querySelectorAll('[data-view="user"]').length,
      stream: doc.querySelectorAll('[data-stream="true"]').length,
      assistant_testid: doc.querySelectorAll('[data-test-id="assistant-message"]').length,
      turns: doc.querySelectorAll('[data-conversation-turn], [class*="conversation-turn"]').length,
      editables: doc.querySelectorAll('[contenteditable="true"]').length,
      composer: !!findComposer(doc)
    };
    const found = candidates.user_view + candidates.stream + candidates.assistant_testid + candidates.turns;
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
    id: "claude",
    label: "Claude",
    domains: ["claude.ai"],
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
