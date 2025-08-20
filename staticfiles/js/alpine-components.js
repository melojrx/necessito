/**
 * Alpine.js Components for Indicai
 * Simple component definitions to avoid loading order issues
 */

// Initialize Alpine components when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Only proceed if Alpine is available
    if (typeof window.Alpine !== 'undefined') {
        initializeAlpineComponents();
    } else {
        // Wait for Alpine to load
        document.addEventListener('alpine:init', initializeAlpineComponents);
    }
});

function initializeAlpineComponents() {
    console.log('Initializing Alpine components');
    
    // Wait for Alpine to be fully loaded
    if (typeof Alpine === 'undefined' || !Alpine.store) {
        console.log('Alpine not ready, waiting...');
        setTimeout(initializeAlpineComponents, 100);
        return;
    }
    
    // Initialize store if not already present
    try {
        Alpine.store('realtime', {
            connected: false,
            reconnecting: false,
            notifications: [],
            unreadCount: 0,
            necessidades: [],
            orcamentos: [],
            messages: [],
            onlineUsers: new Set(),
            socket: null,
            
            formatTime(timestamp) {
                const date = new Date(timestamp);
                const now = new Date();
                const diff = now - date;
                
                if (diff < 60000) return 'agora';
                if (diff < 3600000) return `${Math.floor(diff / 60000)}m`;
                if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`;
                return date.toLocaleDateString('pt-BR');
            }
        });
        console.log('Alpine store initialized successfully');
    } catch (error) {
        console.error('Failed to initialize Alpine store:', error);
    }
}

// Notification system now uses Bootstrap offcanvas (better mobile experience)

// Simple connection status component
function connectionStatus() {
    return {
        init() {
            console.log('Connection status initialized');
        },
        
        get connected() {
            // Only show as connected if we have a real WebSocket connection
            return this.$store?.realtime?.socket?.readyState === WebSocket.OPEN || false;
        },
        
        get reconnecting() {
            return this.$store?.realtime?.reconnecting || false;
        },
        
        get showStatus() {
            // Only show status if we're actually trying to connect or have connection issues
            return this.reconnecting || (!this.connected && this.$store?.realtime?.socket);
        },
        
        retry() {
            console.log('Retry connection');
            if (this.$store?.realtime?.connectWebSocket) {
                this.$store.realtime.connectWebSocket();
            }
        }
    };
}

// Simple necessity card component
function necessidadeCard(necessidade = {}) {
    return {
        data: necessidade,
        
        init() {
            console.log('Necessity card initialized for:', this.data.id);
        },
        
        getStatusClass() {
            return `status-${this.data.status || 'unknown'}`;
        },
        
        getProgressPercentage() {
            const statusSteps = ['criada', 'em_analise', 'orcamentos_recebidos', 'em_negociacao', 'finalizada'];
            const currentIndex = statusSteps.indexOf(this.data.status);
            return currentIndex >= 0 ? ((currentIndex + 1) / statusSteps.length) * 100 : 0;
        }
    };
}

// Make components available globally
window.connectionStatus = connectionStatus;
window.necessidadeCard = necessidadeCard;

console.log('Alpine components script loaded');