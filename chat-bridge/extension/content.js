window.__cbv = 3;
(() => {
  if (window.__chatBridgeInstalled) return;
  window.__chatBridgeInstalled = true;

  const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
  let captureTimer = null;
  let polling = false;
  let fallbackKeyCounter = 0;
  const fallbackKeys = new WeakMap();

  function conversationId() {
    const match = location.pathname.match(/\/c\/([^/?#]+)/);
    return match?.[1] || null;
  }

  function messageUnits() {
    // Current ChatGPT DOM (2026-11+): every message unit carries
    // data-chatgpt-search-unit-key="...:user|assistant" plus stable
    // message UUIDs in data-chatgpt-search-message-ids.
    const fresh = [...document.querySelectorAll('[data-chatgpt-search-unit-key]')].map((el) => {
      const key = el.getAttribute('data-chatgpt-search-unit-key') || '';
      const role = /(^|:)(user|assistant)$/.test(key) ? key.split(':').pop() : null;
      const id = (el.getAttribute('data-chatgpt-search-message-ids') || '').split(/\s+/)[0] || '';
      return role ? { node: el, role, id } : null;
    }).filter(Boolean);
    if (fresh.length) return fresh;
    // Legacy DOM fallback
    return [...document.querySelectorAll('[data-message-author-role]')].map((el) => {
      const role = el.getAttribute('data-message-author-role');
      const id = el.getAttribute('data-message-id') || el.closest('[data-message-id]')?.getAttribute('data-message-id') || '';
      return (role === 'user' || role === 'assistant') ? { node: el, role, id } : null;
    }).filter(Boolean);
  }

  function cleanText(node) {
    // Assistant units include a screen-reader label rendered as text.
    return (node.innerText || node.textContent || '').trim().replace(/^ChatGPT said:\s*/i, '').trim();
  }

  function getMessages() {
    return messageUnits().map((unit, index) => {
      const content = cleanText(unit.node);
      if (!content) return null;
      if (!unit.id && !fallbackKeys.has(unit.node)) {
        fallbackKeyCounter += 1;
        fallbackKeys.set(unit.node, `node:${Date.now()}:${fallbackKeyCounter}`);
      }
      return {
        key: unit.id ? `dom:${unit.id}` : fallbackKeys.get(unit.node),
        role: unit.role,
        content: content.slice(0, 60000),
        ordinal: index
      };
    }).filter(Boolean);
  }

  function snapshot() {
    const id = conversationId();
    if (!id) return;
    const messages = getMessages();
    if (!messages.length) return;
    chrome.runtime.sendMessage({
      type: 'CHAT_BRIDGE_SNAPSHOT',
      snapshot: {
        conversation_id: id,
        title: (document.title || 'ChatGPT conversation').replace(/\s*[|·-]\s*ChatGPT\s*$/i, '').slice(0, 300),
        url: location.href,
        messages
      }
    }).catch(() => {});
  }

  function scheduleSnapshot() {
    clearTimeout(captureTimer);
    captureTimer = setTimeout(snapshot, 900);
  }

  function findComposer() {
    // Current DOM: visible ProseMirror editor (role=textbox, aria-label="Ask ChatGPT").
    const editables = [...document.querySelectorAll('.ProseMirror[role="textbox"], [contenteditable="true"][role="textbox"]')]
      .filter(el => el.getBoundingClientRect().height > 0);
    if (editables.length) return editables[editables.length - 1];
    return document.querySelector('#prompt-textarea')
      || document.querySelector('textarea[placeholder]')
      || document.querySelector('[contenteditable="true"]');
  }

  function findSendButton() {
    const byLabel = () => [...document.querySelectorAll('button')].find(button => /send message|send prompt|שלח/i.test(button.getAttribute('aria-label') || button.title || ''));
    return document.querySelector('button[data-testid="send-button"]')
      || byLabel()
      || (function () {
        // Current DOM: the composer footer's primary-action slot swaps mic -> send once there is text.
        const composer = findComposer();
        if (!composer) return null;
        let container = composer;
        for (let i = 0; i < 8 && container.parentElement; i += 1) {
          container = container.parentElement;
          if (container.querySelectorAll('button').length >= 2) break;
        }
        return [...container.querySelectorAll('button')].find(b => b.querySelector('[class*="primary-action"]')) || null;
      })();
  }

  async function insertText(composer, text) {
    const existingDraft = (composer.value ?? composer.innerText ?? composer.textContent ?? '').trim();
    if (existingDraft) {
      throw new Error('The ChatGPT message box already contains an unsent draft. Clear or send that draft before asking the agent to send a message.');
    }
    composer.focus();
    if (composer instanceof HTMLTextAreaElement || composer instanceof HTMLInputElement) {
      const setter = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(composer), 'value')?.set;
      if (setter) setter.call(composer, text); else composer.value = text;
      composer.dispatchEvent(new Event('input', { bubbles: true }));
    } else {
      document.execCommand('insertText', false, text);
      if (!(composer.innerText || '').trim()) {
        composer.textContent = text;
        composer.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: text }));
      }
    }
    await sleep(250);
  }

  async function executeAgentMessage(action) {
    const targetId = conversationId();
    if (!targetId || targetId !== action.conversation_id) {
      throw new Error('The requested conversation is not the active ChatGPT tab. Open that conversation and try again.');
    }
    const composer = findComposer();
    if (!composer) throw new Error('Could not find the ChatGPT message box. The site layout may have changed.');

    const oldAssistantNodes = messageUnits().filter(u => u.role === 'assistant').map(u => u.node);
    const oldLastAssistant = oldAssistantNodes.at(-1);
    const oldText = oldLastAssistant ? cleanText(oldLastAssistant) : '';
    await insertText(composer, action.message);

    const sendButton = findSendButton();
    if (!sendButton || sendButton.disabled) throw new Error('The ChatGPT send button is unavailable or disabled.');
    sendButton.click();
    scheduleSnapshot();

    const deadline = Date.now() + Math.min(Math.max(action.timeout_ms || 90000, 15000), 120000);
    let stableText = '';
    let stableCount = 0;
    while (Date.now() < deadline) {
      await sleep(900);
      const assistants = messageUnits().filter(u => u.role === 'assistant').map(u => u.node);
      const last = assistants.at(-1);
      const text = last ? cleanText(last) : '';
      const stopButton = document.querySelector('button[data-testid="stop-button"], button[aria-label*="Stop"], button[aria-label*="עצור"]');
      const changed = text && (last !== oldLastAssistant || text !== oldText);
      if (changed && !stopButton && text === stableText) stableCount++;
      else stableCount = 0;
      stableText = text;
      if (changed && stableCount >= 2) {
        scheduleSnapshot();
        return text.slice(0, 60000);
      }
    }
    const assistants = messageUnits().filter(u => u.role === 'assistant').map(u => u.node);
    const latest = assistants.at(-1) ? cleanText(assistants.at(-1)) : '';
    if (latest && (latest !== oldText || assistants.at(-1) !== oldLastAssistant)) return latest.slice(0, 60000);
    throw new Error('Timed out waiting for ChatGPT to finish its response. The message may have been sent; check the open tab.');
  }

  async function poll() {
    if (polling) return;
    const id = conversationId();
    if (!id) return;
    polling = true;
    try {
      const response = await chrome.runtime.sendMessage({ type: 'CHAT_BRIDGE_POLL', conversation_id: id });
      if (response?.ok && response.action) {
        try {
          const answer = await executeAgentMessage(response.action);
          await chrome.runtime.sendMessage({ type: 'CHAT_BRIDGE_ACTION_RESULT', result: {
            action_id: response.action.id,
            status: 'completed',
            response: answer
          }});
        } catch (error) {
          await chrome.runtime.sendMessage({ type: 'CHAT_BRIDGE_ACTION_RESULT', result: {
            action_id: response.action.id,
            status: 'failed',
            error: String(error?.message || error)
          }});
        }
      }
    } catch (_) {
      // A local server may be stopped; keep the content script alive and retry.
    } finally {
      polling = false;
    }
  }

  const observer = new MutationObserver(scheduleSnapshot);
  observer.observe(document.documentElement, { childList: true, subtree: true, characterData: true });
  snapshot();
  setInterval(poll, 1600);
  setInterval(() => { if (conversationId()) scheduleSnapshot(); }, 15000);
})();
