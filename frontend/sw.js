const CACHE_NAME = "mani-portfolio-v3";
const APP_SHELL = [
  "/",
  "/static/css/style.css?v=3",
  "/static/js/main.js?v=3",
  "/manifest.webmanifest",
  "/static/icons/icon.svg"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);

  if (request.method !== "GET" || url.origin !== self.location.origin) {
    return;
  }

  if (request.mode === "navigate" && url.pathname !== "/") {
    return;
  }

  if (
    url.pathname.startsWith("/admin/") ||
    url.pathname.startsWith("/tinymce/") ||
    url.pathname.startsWith("/media/") ||
    url.pathname.startsWith("/static/admin/") ||
    url.pathname.startsWith("/static/admin_interface/") ||
    url.pathname.startsWith("/static/tinymce/")
  ) {
    return;
  }

  if (url.pathname.startsWith("/api/")) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached;
      return fetch(request).then((response) => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
        return response;
      });
    })
  );
});
