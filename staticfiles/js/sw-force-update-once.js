/**
 * Script para forçar atualização única do Service Worker
 * Executa apenas uma vez usando localStorage
 */
(function() {
    'use strict';

    const UPDATE_KEY = 'sw_update_v137_done';
    const TARGET_VERSION = 'v1.3.7';

    // Verificar se já atualizou
    if (localStorage.getItem(UPDATE_KEY) === 'true') {
        console.log('[SW Auto-Update] Atualização já realizada anteriormente');
        return;
    }

    console.log('[SW Auto-Update] Verificando Service Worker...');

    if (!('serviceWorker' in navigator)) {
        console.log('[SW Auto-Update] Service Worker não suportado');
        return;
    }

    // Função para forçar atualização
    async function forceUpdate() {
        try {
            console.log('[SW Auto-Update] Iniciando atualização forçada...');

            // 1. Limpar todos os caches
            if ('caches' in window) {
                const cacheNames = await caches.keys();
                console.log('[SW Auto-Update] Removendo', cacheNames.length, 'caches');
                await Promise.all(cacheNames.map(name => caches.delete(name)));
            }

            // 2. Desregistrar todos os service workers
            const registrations = await navigator.serviceWorker.getRegistrations();
            console.log('[SW Auto-Update] Desregistrando', registrations.length, 'service workers');
            await Promise.all(registrations.map(reg => reg.unregister()));

            // 3. Marcar como atualizado
            localStorage.setItem(UPDATE_KEY, 'true');

            // 4. Recarregar página
            console.log('[SW Auto-Update] Atualização concluída. Recarregando página...');
            setTimeout(() => {
                window.location.reload(true);
            }, 1000);

        } catch (error) {
            console.error('[SW Auto-Update] Erro durante atualização:', error);
        }
    }

    // Verificar versão atual do SW
    navigator.serviceWorker.getRegistrations().then(registrations => {
        if (registrations.length === 0) {
            console.log('[SW Auto-Update] Nenhum SW registrado');
            localStorage.setItem(UPDATE_KEY, 'true'); // Marcar como OK
            return;
        }

        // Buscar o arquivo sw.js para verificar versão
        fetch('/sw.js?v=' + Date.now())
            .then(response => response.text())
            .then(text => {
                // Extrair versão do arquivo
                const versionMatch = text.match(/VERSION\s*=\s*['"]([^'"]+)['"]/);
                if (versionMatch) {
                    const fileVersion = versionMatch[1];
                    console.log('[SW Auto-Update] Versão no arquivo:', fileVersion);

                    if (fileVersion !== TARGET_VERSION) {
                        console.log('[SW Auto-Update] Versão ainda não atualizada no servidor');
                        return;
                    }
                }

                // Se chegou aqui, o arquivo está correto mas o SW ativo pode estar desatualizado
                console.log('[SW Auto-Update] Forçando atualização do Service Worker');
                forceUpdate();
            })
            .catch(error => {
                console.error('[SW Auto-Update] Erro ao verificar versão:', error);
            });
    });

    console.log('[SW Auto-Update] Script carregado');
})();
