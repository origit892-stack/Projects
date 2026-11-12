// Lumio 4.0 — service worker. SHELL ONLY: caches static shell files.
// Never cache API responses, feed content or any student data: everything
// else is network-first with a fallback to the shell.
const CACHE='lumio-shell-v4.0';const ASSETS=['/','/index.html','/app.mjs','/core.mjs','/study.mjs','/importers.mjs','/connectors.mjs','/config.mjs','/style.css','/public/icon.svg'];self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting())));self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));self.addEventListener('fetch',e=>{if(e.request.method!=='GET'||new URL(e.request.url).origin!==location.origin)return;e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)))});
