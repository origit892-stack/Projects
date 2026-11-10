const statusEl = document.getElementById('status');
const conversationEl = document.getElementById('conversation');
const allowSendEl = document.getElementById('allowSend');

async function init() {
  const cfg = await chrome.storage.local.get({ token: '', allowAgentSend: false, lastConversation: null, lastError: '' });
  allowSendEl.checked = cfg.allowAgentSend;
  if (cfg.lastConversation) {
    conversationEl.textContent = `${cfg.lastConversation.title || 'Untitled'}\n${cfg.lastConversation.id}`;
  }
  if (!cfg.token) {
    statusEl.className = 'status bad';
    statusEl.textContent = 'Setup needed: add your local token in Settings.';
    return;
  }
  try {
    const result = await chrome.runtime.sendMessage({ type: 'CHAT_BRIDGE_HEALTH' });
    if (result?.ok) {
      statusEl.className = 'status ok';
      statusEl.textContent = `Local bridge connected · ${result.conversation_count} saved conversations`;
    } else throw new Error(result?.error || cfg.lastError || 'Connection failed');
  } catch (error) {
    statusEl.className = 'status bad';
    statusEl.textContent = `Bridge unavailable: ${error.message}`;
  }
}

allowSendEl.addEventListener('change', async () => {
  await chrome.storage.local.set({ allowAgentSend: allowSendEl.checked });
});
document.getElementById('settings').addEventListener('click', () => chrome.runtime.openOptionsPage());
init();
