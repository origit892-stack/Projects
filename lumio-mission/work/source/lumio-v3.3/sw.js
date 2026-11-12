// Lumio 4.1 — service worker. SHELL ONLY: caches static shell files.
// Lives at the SITE ROOT so its default scope covers the whole app
// (a SW inside public/ is capped to public/ — browsers enforce the max
// scope as the script's own directory; GitHub Pages can't add the
// Service-Worker-Allowed header to extend it).
// Paths are relative to THIS file (the site root) so the app works from
// any subpath (GitHub Pages serves it at /lumio-site/, not /).
const CACHE='lumio-shell-v4.2';const ASSETS=['.','index.html','app.mjs','core.mjs','study.mjs','importers.mjs','connectors.mjs','config.mjs','style.css','public/icon.svg'];self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting())));self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));self.addEventListener('fetch',e=>{if(e.request.method!=='GET'||new URL(e.request.url).origin!==location.origin)return;e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)))});
