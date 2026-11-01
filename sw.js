// True Part Fabrication: offline support. Pages: network first, then cache. Assets: cache first.
const V = 'tpf-1793556804';
const PRE = ['/', '/tools/hose-size-finder/', '/sizes/', '/my-shop/', '/tools/inch-mm-converter/', '/tools/will-it-fit/', '/request-list/', '/assets/models.json'];
self.addEventListener('install', e => { e.waitUntil(caches.open(V).then(c => c.addAll(PRE)).catch(() => {})); self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const r = e.request; if (r.method !== 'GET') return;
  const u = new URL(r.url); if (u.origin !== location.origin) return;
  if (r.mode === 'navigate' || (r.headers.get('accept') || '').includes('text/html')) {
    e.respondWith(fetch(r).then(res => { const cp = res.clone(); if (res.ok) caches.open(V).then(c => c.put(r, cp)); return res; })
      .catch(() => caches.match(r).then(m => m || caches.match('/')).then(m => m || new Response('<h1>Offline</h1><p>You are offline. Pages you opened before are still available.</p>', {headers: {'Content-Type': 'text/html'}}))));
    return;
  }
  if (u.pathname.startsWith('/assets/')) {
    e.respondWith(caches.match(r).then(m => m || fetch(r).then(res => { const cp = res.clone(); if (res.ok) caches.open(V).then(c => c.put(r, cp)); return res; })));
  }
});
