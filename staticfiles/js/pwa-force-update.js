// Script para forçar atualização do PWA e limpeza de cache
function forcePWAUpdate() {
    console.log('[PWA Update] Iniciando atualização forçada...');
    
    // 1. Limpar todos os caches do service worker
    if ('caches' in window) {
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    console.log('[PWA Update] Removendo cache:', cacheName);
                    return caches.delete(cacheName);
                })
            );
        }).then(() => {
            console.log('[PWA Update] Todos os caches removidos');
        });
    }
    
    // 2. Desregistrar service worker atual
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistrations().then(registrations => {
            registrations.forEach(registration => {
                console.log('[PWA Update] Desregistrando SW:', registration.scope);
                registration.unregister();
            });
        });
    }
    
    // 3. Aguardar um pouco e recarregar a página
    setTimeout(() => {
        console.log('[PWA Update] Recarregando página...');
        window.location.reload(true);
    }, 2000);
}

// Registrar SW atualizado no caminho correto
function registerNewServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js', { scope: '/' })
            .then(registration => {
                console.log('[PWA Update] SW registrado:', registration.scope);
            })
            .catch(error => {
                console.error('[PWA Update] Falha no registro:', error);
            });
    }
}

// Adicionar à janela global para uso via console
window.forcePWAUpdate = forcePWAUpdate;
window.registerNewServiceWorker = registerNewServiceWorker;

console.log('[PWA Update Script] Carregado. Use forcePWAUpdate() para forçar atualização.');
