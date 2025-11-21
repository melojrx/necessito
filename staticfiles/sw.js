/**
 * Service Worker for Indicai Marketplace
 * Provides advanced caching and offline capabilities
 */

// Versão da aplicação para controle de atualização forçada
const VERSION = 'v1.3.7';
// NomES de caches versionados (alterar VERSION dispara renovação)
const STATIC_CACHE = `indicai-static-${VERSION}`;
const DYNAMIC_CACHE = `indicai-dynamic-${VERSION}`;
const API_CACHE = `indicai-api-${VERSION}`;

// Files to cache immediately
const STATIC_ASSETS = [
    '/',
    '/static/css/necessity-cards.css',
    '/static/css/mobile-navigation.css',
    '/static/js/performance-optimizations.js',
    '/static/img/logo.png',
    '/static/img/favicon.ico',
    '/offline.html'
];

// External resources to cache on demand
const EXTERNAL_RESOURCES = [
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js'
];

// Cache strategies for different types of requests
const CACHE_STRATEGIES = {
    // Static assets: Cache first
    static: ['css', 'js', 'woff2', 'woff', 'ttf', 'eot'],
    
    // Images: Cache first with fallback
    images: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'ico'],
    
    // API calls: Network first with cache fallback
    api: ['/api/'],
    
    // Pages: Network first with cache fallback
    pages: ['/', '/necessidades/', '/orcamentos/']
};

// Install Service Worker
self.addEventListener('install', event => {
    console.log('Service Worker installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('Caching static assets...');
                const cachePromises = STATIC_ASSETS.map(asset => {
                    return cache.add(asset).catch(err => {
                        console.warn(`[SW] Failed to cache ${asset}:`, err);
                    });
                });
                return Promise.all(cachePromises);
            })
            .then(() => {
                console.log('Static assets cached successfully (with potential individual failures).');
                return self.skipWaiting(); // Force activation
            })
            .catch(error => {
                console.error('Failed to cache static assets:', error);
            })
    );
});

// Activate Service Worker
self.addEventListener('activate', event => {
    console.log('Service Worker activating...');
    
    event.waitUntil(
        Promise.all([
            // Clean up old caches
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && 
                            cacheName !== DYNAMIC_CACHE && 
                            cacheName !== API_CACHE) {
                            console.log('Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            }),
            
            // Take control of all clients
            self.clients.claim(),
            
            // Cache external resources in background
            cacheExternalResources()
        ])
    );
});

// Fetch Event Handler
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Skip chrome extensions and other protocols
    if (!url.protocol.startsWith('http')) {
        return;
    }

    // Skip critical external resources that should never be cached or intercepted
    const criticalExternalDomains = [
        'code.jquery.com',
        'cdn.jsdelivr.net',
        'cdnjs.cloudflare.com',
        'fonts.googleapis.com',
        'fonts.gstatic.com',
        'google.com',
        'gstatic.com',
        'googlesyndication.com',
        'doubleclick.net',
        'googleads.g.doubleclick.net',
        'adservice.google.com',
        'fundingchoicesmessages.google.com'
    ];

    if (criticalExternalDomains.some(domain => url.hostname.includes(domain))) {
        // Let browser handle these requests normally without ServiceWorker intervention
        return;
    }

    event.respondWith(handleFetch(request));
});

async function handleFetch(request) {
    const url = new URL(request.url);
    const extension = getFileExtension(url.pathname);
    
    try {
        // For authenticated pages (containing user account paths), prefer network
        if (url.pathname.includes('/users/') || url.pathname.includes('/minha-conta/')) {
            return await networkFirst(request, DYNAMIC_CACHE, { timeoutMs: 8000, prune: true });
        }
        
        // Determine cache strategy based on request type
        if (CACHE_STRATEGIES.static.includes(extension)) {
            return await cacheFirst(request, STATIC_CACHE);
        }
        if (CACHE_STRATEGIES.images.includes(extension)) {
            return await cacheFirst(request, DYNAMIC_CACHE, { prune: true });
        }
        if (CACHE_STRATEGIES.api.some(pattern => url.pathname.startsWith(pattern))) {
            return await networkFirst(request, API_CACHE, { timeoutMs: 5000, prune: true });
        }
        if (url.origin === self.location.origin) {
            return await networkFirst(request, DYNAMIC_CACHE, { timeoutMs: 8000, prune: true });
        }
        // External: network first com timeout
        return await networkFirst(request, DYNAMIC_CACHE, { timeoutMs: 5000, prune: true });
        
    } catch (error) {
        console.error('Fetch error:', error);
        return await handleFetchError(request, error);
    }
}

// Cache First Strategy
async function cacheFirst(request, cacheName, options = {}) {
    const cache = await caches.open(cacheName);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
        // Return cached version and update in background
        updateCache(request, cache);
        return cachedResponse;
    }
    
    // If not in cache, fetch from network
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
            if (options.prune) {
                pruneCache(cacheName, cacheName === DYNAMIC_CACHE ? 100 : 60);
            }
        }
        return networkResponse;
    } catch (error) {
        throw error;
    }
}

// Network First Strategy
async function networkFirst(request, cacheName, { timeoutMs = 8000, prune = false } = {}) {
    const cache = await caches.open(cacheName);
    
    const networkPromise = (async () => {
        const response = await fetch(request);
        if (response.ok) {
            cache.put(request, response.clone());
            if (prune) {
                pruneCache(cacheName, cacheName === API_CACHE ? 80 : 120);
            }
        }
        return response;
    })();
    
    const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error('Network timeout')), timeoutMs));
    
    try {
        return await Promise.race([networkPromise, timeoutPromise]);
    } catch (error) {
        const cachedResponse = await cache.match(request);
        if (cachedResponse) return cachedResponse;
        throw error;
    }
}

// Update cache in background
async function updateCache(request, cache) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
        }
    } catch (error) {
        // Ignore background update errors
        console.warn('Background cache update failed:', error);
    }
}

// Handle fetch errors with appropriate fallbacks
async function handleFetchError(request, error) {
    const url = new URL(request.url);
    
    // Only show offline page for main navigation requests, not for assets
    const isMainPageRequest = request.headers.get('Accept')?.includes('text/html') && 
                             request.mode === 'navigate' &&
                             !url.pathname.includes('/static/') &&
                             !url.pathname.includes('/media/');
    
    if (isMainPageRequest) {
        // Check if we have a cached version of the page first
        const cache = await caches.open(DYNAMIC_CACHE);
        const cachedResponse = await cache.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Only return offline page as last resort
        const offlineCache = await caches.open(STATIC_CACHE);
        const offlinePage = await offlineCache.match('/offline.html');
        return offlinePage || createOfflineResponse();
    }
    
    // For images, return placeholder only if it's actually an image request
    if (CACHE_STRATEGIES.images.includes(getFileExtension(url.pathname))) {
        return createImagePlaceholder();
    }
    
    // For API calls, return error response
    if (CACHE_STRATEGIES.api.some(pattern => url.pathname.startsWith(pattern))) {
        return createAPIErrorResponse();
    }
    
    // For other assets (favicon, etc), fail silently
    if (url.pathname.includes('/favicon.ico') || url.pathname.includes('/static/')) {
        return new Response('', { status: 404 });
    }
    
    // Default: re-throw error
    throw error;
}

// Utility Functions
function getFileExtension(pathname) {
    const parts = pathname.split('.');
    return parts.length > 1 ? parts.pop().toLowerCase() : '';
}

function createOfflineResponse() {
    const html = `
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Offline - Indicai</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-align: center;
                }
                .offline-container {
                    max-width: 400px;
                    padding: 2rem;
                }
                .offline-icon {
                    font-size: 4rem;
                    margin-bottom: 1rem;
                }
                h1 {
                    margin-bottom: 1rem;
                }
                .retry-btn {
                    background: white;
                    color: #667eea;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-weight: bold;
                    margin-top: 1rem;
                }
            </style>
        </head>
        <body>
            <div class="offline-container">
                <div class="offline-icon">📴</div>
                <h1>Você está offline</h1>
                <p>Não foi possível conectar à internet. Verifique sua conexão e tente novamente.</p>
                <button class="retry-btn" onclick="window.location.reload()">
                    Tentar Novamente
                </button>
            </div>
        </body>
        </html>
    `;
    
    return new Response(html, {
        headers: { 'Content-Type': 'text/html' }
    });
}

function createImagePlaceholder() {
    // Create a simple SVG placeholder instead of data URI
    const svgPlaceholder = `<svg width="1" height="1" xmlns="http://www.w3.org/2000/svg"><rect width="1" height="1" fill="transparent"/></svg>`;
    return new Response(svgPlaceholder, { 
        headers: { 'Content-Type': 'image/svg+xml' } 
    });
}

function createAPIErrorResponse() {
    return new Response(JSON.stringify({
        error: 'Network unavailable',
        message: 'You are currently offline. Please check your connection.',
        offline: true
    }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
    });
}

// Background Sync for form submissions
self.addEventListener('sync', event => {
    if (event.tag === 'background-sync') {
        event.waitUntil(handleBackgroundSync());
    }
});

async function handleBackgroundSync() {
    // Handle any pending form submissions or data syncing
    console.log('Background sync triggered');
    
    try {
        // Sync pending data from IndexedDB
        await syncPendingData();
    } catch (error) {
        console.error('Background sync failed:', error);
    }
}

async function syncPendingData() {
    // This would sync any pending form submissions, messages, etc.
    // Implementation depends on your offline data storage strategy
}

// Push Notifications
self.addEventListener('push', event => {
    if (event.data) {
        const data = event.data.json();
        
        const options = {
            body: data.body,
            icon: '/static/img/logo.png',
            badge: '/static/img/badge.png',
            data: data.data,
            actions: data.actions || [],
            requireInteraction: data.requireInteraction || false
        };
        
        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

// Notification click handler
self.addEventListener('notificationclick', event => {
    event.notification.close();
    
    const data = event.notification.data;
    const action = event.action;
    
    if (action === 'open' || !action) {
        const url = data?.url || '/';
        event.waitUntil(
            clients.openWindow(url)
        );
    }
});

// Cache Management
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_URLS') {
        event.waitUntil(
            cacheUrls(event.data.urls)
        );
    }
});

async function cacheUrls(urls) {
    const cache = await caches.open(DYNAMIC_CACHE);
    return cache.addAll(urls);
}

// Limpeza simples por tamanho máximo (FIFO baseada na ordem de inserção)
async function pruneCache(cacheName, maxEntries = 100) {
    try {
        const cache = await caches.open(cacheName);
        const keys = await cache.keys();
        if (keys.length > maxEntries) {
            const excess = keys.length - maxEntries;
            for (let i = 0; i < excess; i++) {
                await cache.delete(keys[i]);
            }
            console.log(`[SW] pruneCache(${cacheName}) removed ${excess} entries (now <= ${maxEntries})`);
        }
    } catch (e) {
        console.warn('[SW] pruneCache error', e);
    }
}

// Cache external resources in background
async function cacheExternalResources() {
    try {
        const cache = await caches.open(STATIC_CACHE);
        const cachePromises = EXTERNAL_RESOURCES.map(async (resource) => {
            try {
                const response = await fetch(resource);
                if (response.ok) {
                    await cache.put(resource, response);
                    console.log(`[SW] Cached external resource: ${resource}`);
                }
            } catch (error) {
                console.warn(`[SW] Failed to cache external resource ${resource}:`, error);
            }
        });
        await Promise.allSettled(cachePromises);
    } catch (error) {
        console.warn('[SW] Error caching external resources:', error);
    }
}

console.log('Service Worker loaded successfully');