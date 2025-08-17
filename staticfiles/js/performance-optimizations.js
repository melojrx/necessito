/**
 * Performance Optimizations
 * - Lazy Loading for images and content
 * - Intersection Observer for cards
 * - Local Storage caching
 * - Preloading critical resources
 */

class PerformanceOptimizer {
    constructor() {
        this.imageObserver = null;
        this.contentObserver = null;
        this.cache = new Map();
        this.init();
    }

    init() {
        this.setupImageLazyLoading();
        this.setupContentLazyLoading();
        this.setupPreloading();
        this.setupLocalStorageCache();
        this.setupServiceWorkerCache();
    }

    /**
     * Lazy Loading for Images
     */
    setupImageLazyLoading() {
        // Create intersection observer for images
        if ('IntersectionObserver' in window) {
            this.imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        this.loadImage(img);
                        this.imageObserver.unobserve(img);
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.1
            });

            // Observe all lazy images
            this.observeLazyImages();
        } else {
            // Fallback for older browsers
            this.loadAllImages();
        }
    }

    observeLazyImages() {
        const lazyImages = document.querySelectorAll('img[data-src]:not([src])');
        lazyImages.forEach(img => {
            this.imageObserver.observe(img);
        });
    }

    loadImage(img) {
        const src = img.dataset.src;
        if (src) {
            // Add loading animation
            img.classList.add('loading');
            
            // Create new image to preload
            const imageLoader = new Image();
            imageLoader.onload = () => {
                img.src = src;
                img.classList.remove('loading');
                img.classList.add('loaded');
                img.removeAttribute('data-src');
            };
            imageLoader.onerror = () => {
                img.classList.remove('loading');
                img.classList.add('error');
                // Set fallback image
                img.src = '/static/img/placeholder.png';
            };
            imageLoader.src = src;
        }
    }

    loadAllImages() {
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => this.loadImage(img));
    }

    /**
     * Lazy Loading for Content Cards
     */
    setupContentLazyLoading() {
        if ('IntersectionObserver' in window) {
            this.contentObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const card = entry.target;
                        this.loadCardContent(card);
                        this.contentObserver.unobserve(card);
                    }
                });
            }, {
                rootMargin: '100px 0px',
                threshold: 0.1
            });

            // Observe cards that need lazy loading
            this.observeLazyCards();
        }
    }

    observeLazyCards() {
        const lazyCards = document.querySelectorAll('.card[data-lazy-load]');
        lazyCards.forEach(card => {
            this.contentObserver.observe(card);
        });
    }

    loadCardContent(card) {
        const url = card.dataset.lazyLoad;
        if (url && !card.classList.contains('loaded')) {
            card.classList.add('loading');
            
            fetch(url)
                .then(response => response.text())
                .then(html => {
                    const contentContainer = card.querySelector('.lazy-content');
                    if (contentContainer) {
                        contentContainer.innerHTML = html;
                    }
                    card.classList.remove('loading');
                    card.classList.add('loaded');
                })
                .catch(error => {
                    console.error('Error loading card content:', error);
                    card.classList.remove('loading');
                    card.classList.add('error');
                });
        }
    }

    /**
     * Preloading Critical Resources
     */
    setupPreloading() {
        // Only preload resources that will actually be used immediately
        // Remove excessive preloading to avoid browser warnings
        
        // Preload next page resources on hover
        this.setupHoverPreloading();
    }

    preloadResource(href, as, crossorigin = null) {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = href;
        link.as = as;
        if (crossorigin) {
            link.crossOrigin = crossorigin;
        }
        document.head.appendChild(link);
    }

    setupHoverPreloading() {
        // Preload page when user hovers over link for 200ms
        let hoverTimeout;
        
        document.addEventListener('mouseover', (e) => {
            const link = e.target.closest('a[href]');
            if (link && this.isInternalLink(link.href)) {
                hoverTimeout = setTimeout(() => {
                    this.preloadPage(link.href);
                }, 200);
            }
        });

        document.addEventListener('mouseout', (e) => {
            if (hoverTimeout) {
                clearTimeout(hoverTimeout);
            }
        });
    }

    isInternalLink(url) {
        try {
            const link = new URL(url, window.location.origin);
            return link.origin === window.location.origin;
        } catch {
            return false;
        }
    }

    preloadPage(url) {
        if (!this.cache.has(url)) {
            fetch(url, { method: 'HEAD' })
                .then(() => {
                    this.cache.set(url, Date.now());
                })
                .catch(() => {
                    // Ignore errors for preloading
                });
        }
    }

    /**
     * Local Storage Caching
     */
    setupLocalStorageCache() {
        this.cacheUserPreferences();
        this.cacheStaticData();
    }

    cacheUserPreferences() {
        // Cache user preferences for faster loading
        const userPrefs = {
            theme: localStorage.getItem('theme') || 'light',
            language: localStorage.getItem('language') || 'pt-BR',
            location: localStorage.getItem('location'),
            lastVisit: Date.now()
        };

        localStorage.setItem('userPreferences', JSON.stringify(userPrefs));
    }

    cacheStaticData() {
        // Cache static data when available
        // Categories endpoint will be implemented later
        console.log('Static data caching ready for future implementation');
    }

    getCachedData(key, maxAge = 24 * 60 * 60 * 1000) {
        try {
            const cached = localStorage.getItem(key);
            if (cached) {
                const data = JSON.parse(cached);
                if (Date.now() - data.timestamp < maxAge) {
                    return data.data;
                } else {
                    localStorage.removeItem(key);
                }
            }
        } catch (error) {
            console.warn(`Failed to get cached data for ${key}:`, error);
        }
        return null;
    }

    /**
     * Service Worker for Advanced Caching
     */
    setupServiceWorkerCache() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/sw.js')
                .then(registration => {
                    console.log('ServiceWorker registered:', registration);
                })
                .catch(error => {
                    console.warn('ServiceWorker registration failed:', error);
                });
        }
    }

    /**
     * Image Compression for Uploads
     */
    compressImage(file, maxWidth = 800, quality = 0.8) {
        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();

            img.onload = () => {
                // Calculate new dimensions
                let { width, height } = img;
                if (width > maxWidth) {
                    height = (height * maxWidth) / width;
                    width = maxWidth;
                }

                canvas.width = width;
                canvas.height = height;

                // Draw and compress
                ctx.drawImage(img, 0, 0, width, height);
                canvas.toBlob(resolve, 'image/jpeg', quality);
            };

            img.src = URL.createObjectURL(file);
        });
    }

    /**
     * Debounced Search
     */
    createDebouncedSearch(searchFunction, delay = 300) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => searchFunction.apply(this, args), delay);
        };
    }

    /**
     * Virtual Scrolling for Large Lists
     */
    setupVirtualScrolling(container, itemHeight = 100, buffer = 5) {
        if (!container) return;

        const items = Array.from(container.children);
        const totalItems = items.length;
        
        if (totalItems < 20) return; // Not worth it for small lists

        const containerHeight = container.clientHeight;
        const visibleItems = Math.ceil(containerHeight / itemHeight) + buffer * 2;

        let scrollTop = 0;
        let startIndex = 0;

        const updateVisibleItems = () => {
            const newStartIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - buffer);
            const endIndex = Math.min(totalItems, newStartIndex + visibleItems);

            if (newStartIndex !== startIndex) {
                startIndex = newStartIndex;

                // Hide all items first
                items.forEach((item, index) => {
                    if (index < startIndex || index >= endIndex) {
                        item.style.display = 'none';
                    } else {
                        item.style.display = '';
                        item.style.transform = `translateY(${index * itemHeight}px)`;
                    }
                });
            }
        };

        container.addEventListener('scroll', () => {
            scrollTop = container.scrollTop;
            requestAnimationFrame(updateVisibleItems);
        });

        // Initial render
        updateVisibleItems();
    }

    /**
     * Batch DOM Updates
     */
    batchDOMUpdates(updates) {
        requestAnimationFrame(() => {
            updates.forEach(update => {
                if (typeof update === 'function') {
                    update();
                }
            });
        });
    }

    /**
     * Memory Management
     */
    cleanup() {
        if (this.imageObserver) {
            this.imageObserver.disconnect();
        }
        if (this.contentObserver) {
            this.contentObserver.disconnect();
        }
        this.cache.clear();
    }
}

// CSS for loading states
const loadingCSS = `
.loading {
    position: relative;
    overflow: hidden;
}

.loading::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
    animation: loading-shimmer 1.5s infinite;
}

@keyframes loading-shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}

.loaded {
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.error {
    opacity: 0.5;
    filter: grayscale(100%);
}

/* Skeleton loading for cards */
.skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
}

@keyframes skeleton-loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
`;

// Initialize performance optimizer when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Add loading CSS
    const style = document.createElement('style');
    style.textContent = loadingCSS;
    document.head.appendChild(style);

    // Initialize optimizer
    window.performanceOptimizer = new PerformanceOptimizer();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.performanceOptimizer) {
        window.performanceOptimizer.cleanup();
    }
});

// Export for use in other scripts
window.PerformanceOptimizer = PerformanceOptimizer;