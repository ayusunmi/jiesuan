// 便携收银台 Service Worker - 离线缓存
// 兼容 GitHub Pages 子路径部署（如 https://user.github.io/repo/）
const CACHE_NAME = 'pos-cache-v4';

// 核心资源（相对于 SW 文件位置）
const CORE_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './products.js',
];

// 需要运行时缓存的 CDN 资源
const CDN_CACHE_PATTERNS = [
  /cdn\.jsdelivr\.net/,
  /cdnjs\.cloudflare\.com/,
  /unpkg\.com/,
  /cdn\.jsdelivr\.net/,
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(CORE_ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  // 只处理 GET
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // CDN 资源：缓存优先
  if (CDN_CACHE_PATTERNS.some((p) => p.test(url.href))) {
    event.respondWith(
      caches.match(req).then((cached) => {
        if (cached) return cached;
        return fetch(req).then((res) => {
          if (res && res.ok) {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((c) => c.put(req, clone));
          }
          return res;
        }).catch(() => cached);
      })
    );
    return;
  }

  // 同源资源：网络优先，回退缓存（确保更新能及时生效）
  if (url.origin === self.location.origin) {
    event.respondWith(
      fetch(req).then((res) => {
        if (res && res.ok) {
          const clone = res.clone();
          caches.open(CACHE_NAME).then((c) => c.put(req, clone));
        }
        return res;
      }).catch(() => {
        return caches.match(req).then((cached) => {
          return cached || caches.match('./index.html');
        });
      })
    );
    return;
  }
});
