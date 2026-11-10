const $ = (id) => document.getElementById(id);
const PROVIDER_LABELS = { chatgpt: "ChatGPT", claude: "Claude", gemini: "Gemini", grok: "Grok" };

function relativeTime(iso) {
  if (!iso) return "never";
  const then = new Date(iso.endsWith("Z") || iso.includes("+") ? iso : `${iso}Z`);
  if (Number.isNaN(then.getTime())) return iso;
  const seconds = Math.max(0, Math.round((Date.now() - then.getTime()) / 1000));
  if (seconds < 10) return "just now";
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.round(hours / 24)}d ago`;
}

function renderProviders(providers) {
  const el = $("providers");
  el.innerHTML = "";
  const entries = Object.entries(providers || {});
  if (!entries.length) {
    el.innerHTML = "<p class='hint'>No provider conversations captured yet. Open a Chat, Claude, Gemini, or Grok conversation in a tab.</p>";
    return;
  }
  const list = document.createElement("ul");
  list.className = "providers";
  for (const [provider, info] of entries) {
    const li = document.createElement("li");
    li.className = `provider ${info.capture_failed ? "failed" : "ok"}`;
    const name = document.createElement("span");
    name.className = "provider-name";
    name.textContent = info.label || PROVIDER_LABELS[provider] || provider;
    const detail = document.createElement("span");
    detail.className = "provider-detail";
    detail.textContent = `${info.conversations || 0} conv · ${info.messages || 0} msgs · last capture ${relativeTime(info.last_updated)}`;
    li.append(name, detail);
    if (info.capture_failed) {
      const note = document.createElement("span");
      note.className = "provider-note";
      note.textContent = `capture failing — ${info.diag?.reason || "layout changed"}`;
      note.title = JSON.stringify(info.diag?.candidates || {}, null, 2);
      li.append(note);
    }
    list.append(li);
  }
  el.append(list);
}

async function refresh() {
  const statusEl = $("status");
  const retry = $("retry");
  statusEl.className = "card";
  try {
    const health = await chrome.runtime.sendMessage({ type: "CHAT_BRIDGE_HEALTH" });
    if (!health?.ok) throw new Error(health?.error || "daemon unreachable");
    statusEl.classList.add("ok");
    const total = Object.values(health.providers || {}).reduce((n, p) => n + (p.conversations || 0), 0);
    statusEl.textContent = `Local bridge connected · ${health.version || ""} · ${total} conversation${total === 1 ? "" : "s"}`.replace("  ", " ");
    retry.classList.add("hidden");
    $("send-box").classList.remove("hidden");

    const providers = await chrome.runtime.sendMessage({ type: "CHAT_BRIDGE_PROVIDERS" });
    renderProviders(providers?.providers || {});
  } catch (error) {
    // v2 fix for the old "Failed to fetch" dead end: the daemon being down is a
    // first-class state with instructions, not a fetch error.
    statusEl.classList.add("offline");
    statusEl.textContent = "Daemon offline";
    const detail = document.createElement("p");
    detail.className = "hint";
    detail.textContent = "Start it from the project folder:  cd <chat-bridge> && ./start.command   (or: python3 host/bridge_daemon.py)";
    statusEl.append(detail);
    retry.classList.remove("hidden");
    $("providers").innerHTML = "<p class='hint'>Provider status is available once the daemon is running.</p>";
  }
  const cfg = await chrome.storage.local.get({ allowAgentSend: false });
  $("allowSend").checked = Boolean(cfg.allowAgentSend);
}

document.addEventListener("DOMContentLoaded", async () => {
  $("retry").addEventListener("click", refresh);
  $("settings").addEventListener("click", () => { window.open("options.html", "_blank"); });

  const allow = $("allowSend");
  allow.addEventListener("change", async () => {
    await chrome.storage.local.set({ allowAgentSend: allow.checked });
    if (allow.checked) {
      const statusEl = $("status");
      statusEl.classList.add("warn");
      const note = document.createElement("p");
      note.className = "hint warn-note";
      note.textContent = "Enabled — the agent may send in the visible provider tab. Drafts are never touched.";
      statusEl.append(note);
      setTimeout(() => note.remove(), 4000);
    }
  });

  $("rotate").addEventListener("click", async () => {
    const result = await chrome.runtime.sendMessage({ type: "CHAT_BRIDGE_ROTATE" });
    $("last-error").classList.remove("hidden");
    $("last-error").textContent = result?.ok
      ? "Token rotated. Paste the new token into the extension settings if prompted."
      : `Rotation failed: ${result?.error || "daemon offline"}`;
    setTimeout(() => $("last-error").classList.add("hidden"), 6000);
  });

  const cfg = await chrome.storage.local.get({ token: "" });
  if (!cfg.token) {
    const statusEl = $("status");
    statusEl.classList.add("offline");
    statusEl.textContent = "Token missing";
    const detail = document.createElement("p");
    detail.className = "hint";
    detail.textContent = "Open Settings and paste the token the installer created.";
    statusEl.append(detail);
    return;
  }
  await refresh();
});
