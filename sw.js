const CACHE = 'panel-shell-v1';
const SHELL = ['./', './index.html', './manifest.json'];

self.addEventListener('install', (e)=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', (e)=>{ self.clients.claim(); });

self.addEventListener('fetch', (e)=>{
  const url = new URL(e.request.url);
  // always go to network for live data files, fall back to cache
  if(url.pathname.includes('/data/')){
    e.respondWith(
      fetch(e.request).then(r=>{
        const clone = r.clone();
        caches.open(CACHE).then(c=>c.put(e.request, clone));
        return r;
      }).catch(()=>caches.match(e.request))
    );
    return;
  }
  // shell files: cache-first
  e.respondWith(caches.match(e.request).then(r=>r || fetch(e.request)));
});
