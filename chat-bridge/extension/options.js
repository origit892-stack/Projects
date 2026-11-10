const token = document.getElementById('token');
const saved = document.getElementById('saved');
chrome.storage.local.get({ token: '' }).then(cfg => { token.value = cfg.token; });
document.getElementById('save').addEventListener('click', async () => {
  const value = token.value.trim();
  if (value.length < 32) { saved.style.color = '#b91c1c'; saved.textContent = 'Token looks too short. Copy the full token from install_mac.sh.'; return; }
  await chrome.storage.local.set({ token: value });
  saved.style.color = '#047857'; saved.textContent = 'Saved. Reload your provider tabs (ChatGPT, Claude, Gemini, Grok) to start capturing.';
});
