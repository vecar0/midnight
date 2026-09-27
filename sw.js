// 자정까지 — 오프라인에서도 열리도록. 인터넷이 되면 새 버전을 먼저 받아온다.
// GitHub Pages는 https://아이디.github.io/저장소이름/ 아래에서 열리므로 모든 경로를 상대 경로로 둔다.
const CACHE = 'midnight-v10';
const FILES = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './apple-touch-icon.png', './favicon.ico'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES))); self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))); self.clients.claim(); });
self.addEventListener('fetch', e => {
  const req = e.request; if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) {
    e.respondWith(caches.match(req).then(r => r || fetch(req).then(res => { const cp = res.clone(); caches.open(CACHE).then(c => c.put(req, cp)); return res; }).catch(() => r)));
    return;
  }
  e.respondWith(fetch(req).then(res => { const cp = res.clone(); caches.open(CACHE).then(c => c.put(req, cp)); return res; })
    .catch(() => caches.match(req).then(r => r || caches.match('./index.html'))));
});
