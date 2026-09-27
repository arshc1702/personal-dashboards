const CACHE = 'panel-shell-v3';
const SHELL = ['./', './index.html', './manifest.json'];

self.addEventListener('install', (e)=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', (e)=>{
  // drop caches from older versions so a stale shell can't linger
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e)=>{
  const url = new URL(e.request.url);
  // only handle this site's own GETs — GitHub API calls, fonts and bean
  // photos go straight to the network untouched
  if(e.request.method !== 'GET' || url.origin !== self.location.origin) return;
  // network first (so updates reach the always-on iPad), cache as the offline fallback
  e.respondWith(
    fetch(e.request).then(r=>{
      if(r.ok){
        const clone = r.clone();
        caches.open(CACHE).then(c=>c.put(e.request, clone));
      }
      return r;
    }).catch(()=>caches.match(e.request))
  );
});
