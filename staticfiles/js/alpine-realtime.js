/**
 * Alpine.js Real-Time Updates for Indicai
 * Provides reactive components and real-time functionality
 */

// Debug logging
console.log('Alpine Real-time script loaded');

// Alpine.js Global Store for Real-Time Data
document.addEventListener('alpine:init', () => {
    console.log('Alpine:init event fired');
    Alpine.store('realtime', {
        // Connection status
        connected: false,
        reconnecting: false,
        
        // Real-time data
        notifications: [],
        unreadCount: 0,
        necessidades: [],
        orcamentos: [],
        messages: [],
        
        // User presence
        onlineUsers: new Set(),
        
        // WebSocket connection
        socket: null,
        
        // Initialize real-time connection
        init() {
            this.connectWebSocket();
            this.loadInitialData();
            this.setupHeartbeat();
        },
        
        // WebSocket connection
        connectWebSocket() {
            const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
            const wsPath = `${wsScheme}://${window.location.host}/ws/realtime/`;
            
            try {
                this.socket = new WebSocket(wsPath);
                
                this.socket.onopen = () => {
                    this.connected = true;
                    this.reconnecting = false;
                    console.log('WebSocket connected');
                    this.sendUserPresence();
                };
                
                this.socket.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                };
                
                this.socket.onclose = () => {
                    this.connected = false;
                    console.log('WebSocket disconnected');
                    this.attemptReconnection();
                };
                
                this.socket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    this.connected = false;
                };
                
            } catch (error) {
                console.error('Failed to connect WebSocket:', error);
                this.setupPolling(); // Fallback to polling
            }
        },
        
        // Handle incoming WebSocket messages
        handleMessage(data) {
            switch (data.type) {
                case 'notification':
                    this.addNotification(data.payload);
                    break;
                case 'necessidade_update':
                    this.updateNecessidade(data.payload);
                    break;
                case 'orcamento_update':
                    this.updateOrcamento(data.payload);
                    break;
                case 'user_presence':
                    this.updateUserPresence(data.payload);
                    break;
                case 'message':
                    this.addMessage(data.payload);
                    break;
                case 'heartbeat':
                    this.handleHeartbeat(data.payload);
                    break;
            }
        },
        
        // Send user presence
        sendUserPresence() {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({
                    type: 'user_presence',
                    payload: {
                        user_id: window.currentUserId || null,
                        status: 'online',
                        timestamp: Date.now()
                    }
                }));
            }
        },
        
        // Add notification
        addNotification(notification) {
            this.notifications.unshift({
                ...notification,
                id: Date.now(),
                timestamp: new Date(),
                read: false
            });
            
            this.unreadCount++;
            
            // Show browser notification if permission granted
            this.showBrowserNotification(notification);
            
            // Update UI
            this.updateNotificationBadge();
        },
        
        // Update necessidade
        updateNecessidade(necessidade) {
            const index = this.necessidades.findIndex(n => n.id === necessidade.id);
            if (index !== -1) {
                this.necessidades[index] = { ...this.necessidades[index], ...necessidade };
            } else {
                this.necessidades.unshift(necessidade);
            }
            
            // Update DOM if on necessidades page
            this.updateNecessidadeCard(necessidade);
        },
        
        // Update orcamento
        updateOrcamento(orcamento) {
            const index = this.orcamentos.findIndex(o => o.id === orcamento.id);
            if (index !== -1) {
                this.orcamentos[index] = { ...this.orcamentos[index], ...orcamento };
            } else {
                this.orcamentos.unshift(orcamento);
            }
            
            // Update DOM if on orcamentos page
            this.updateOrcamentoCard(orcamento);
        },
        
        // Update user presence
        updateUserPresence(presence) {
            if (presence.status === 'online') {
                this.onlineUsers.add(presence.user_id);
            } else {
                this.onlineUsers.delete(presence.user_id);
            }
            
            // Update user status indicators
            this.updateUserStatusIndicators();
        },
        
        // Add chat message
        addMessage(message) {
            this.messages.push({
                ...message,
                timestamp: new Date(message.timestamp)
            });
            
            // Update chat UI if chat is open
            this.updateChatUI(message);
        },
        
        // Load initial data
        async loadInitialData() {
            try {
                // Load notifications
                const notificationsResponse = await fetch('/api/v1/notifications/');
                if (notificationsResponse.ok) {
                    const notifications = await notificationsResponse.json();
                    this.notifications = notifications.results || [];
                    this.unreadCount = notifications.results?.filter(n => !n.read).length || 0;
                }
                
                // Load recent necessidades if on necessidades page
                if (window.location.pathname.includes('/necessidades/')) {
                    const necessidadesResponse = await fetch('/api/v1/necessidades/');
                    if (necessidadesResponse.ok) {
                        const necessidades = await necessidadesResponse.json();
                        this.necessidades = necessidades.results || [];
                    }
                }
                
            } catch (error) {
                console.error('Failed to load initial data:', error);
            }
        },
        
        // Attempt reconnection
        attemptReconnection() {
            if (!this.reconnecting) {
                this.reconnecting = true;
                
                setTimeout(() => {
                    if (!this.connected) {
                        console.log('Attempting to reconnect...');
                        this.connectWebSocket();
                    }
                }, 3000);
            }
        },
        
        // Setup polling fallback
        setupPolling() {
            console.log('Setting up polling fallback');
            
            setInterval(async () => {
                try {
                    // Poll for notifications
                    const response = await fetch('/api/v1/notifications/unread/');
                    if (response.ok) {
                        const data = await response.json();
                        
                        // Check for new notifications
                        data.forEach(notification => {
                            if (!this.notifications.find(n => n.id === notification.id)) {
                                this.addNotification(notification);
                            }
                        });
                    }
                } catch (error) {
                    console.warn('Polling failed:', error);
                }
            }, 30000); // Poll every 30 seconds
        },
        
        // Setup heartbeat
        setupHeartbeat() {
            setInterval(() => {
                if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                    this.socket.send(JSON.stringify({
                        type: 'heartbeat',
                        payload: { timestamp: Date.now() }
                    }));
                }
            }, 30000); // Send heartbeat every 30 seconds
        },
        
        // Handle heartbeat response
        handleHeartbeat(payload) {
            const latency = Date.now() - payload.timestamp;
            console.log(`WebSocket latency: ${latency}ms`);
        },
        
        // Show browser notification
        async showBrowserNotification(notification) {
            if ('Notification' in window && Notification.permission === 'granted') {
                new Notification(notification.title || 'Nova notificação', {
                    body: notification.message,
                    icon: '/static/img/logo.png',
                    badge: '/static/img/badge.png',
                    tag: `notification-${notification.id}`,
                    requireInteraction: false,
                    silent: false
                });
            }
        },
        
        // Update notification badge
        updateNotificationBadge() {
            const badges = document.querySelectorAll('.notification-badge');
            badges.forEach(badge => {
                if (this.unreadCount > 0) {
                    badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
                    badge.style.display = 'block';
                } else {
                    badge.style.display = 'none';
                }
            });
        },
        
        // Update necessidade card in DOM
        updateNecessidadeCard(necessidade) {
            const card = document.querySelector(`[data-necessidade-id="${necessidade.id}"]`);
            if (card) {
                // Update status
                const statusElement = card.querySelector('.necessidade-status');
                if (statusElement) {
                    statusElement.textContent = necessidade.status;
                    statusElement.className = `necessidade-status status-${necessidade.status}`;
                }
                
                // Update orcamento count
                const countElement = card.querySelector('.orcamento-count');
                if (countElement && necessidade.orcamento_count !== undefined) {
                    countElement.textContent = `${necessidade.orcamento_count} orçamentos`;
                }
                
                // Add update animation
                card.classList.add('updated');
                setTimeout(() => card.classList.remove('updated'), 2000);
            }
        },
        
        // Update orcamento card in DOM
        updateOrcamentoCard(orcamento) {
            const card = document.querySelector(`[data-orcamento-id="${orcamento.id}"]`);
            if (card) {
                // Update status
                const statusElement = card.querySelector('.orcamento-status');
                if (statusElement) {
                    statusElement.textContent = orcamento.status;
                    statusElement.className = `orcamento-status status-${orcamento.status}`;
                }
                
                // Add update animation
                card.classList.add('updated');
                setTimeout(() => card.classList.remove('updated'), 2000);
            }
        },
        
        // Update user status indicators
        updateUserStatusIndicators() {
            const indicators = document.querySelectorAll('[data-user-status]');
            indicators.forEach(indicator => {
                const userId = parseInt(indicator.dataset.userId);
                const isOnline = this.onlineUsers.has(userId);
                
                indicator.classList.toggle('online', isOnline);
                indicator.classList.toggle('offline', !isOnline);
                indicator.title = isOnline ? 'Online' : 'Offline';
            });
        },
        
        // Update chat UI
        updateChatUI(message) {
            const chatContainer = document.querySelector('#chat-messages');
            if (chatContainer) {
                const messageElement = this.createMessageElement(message);
                chatContainer.appendChild(messageElement);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        },
        
        // Create message element
        createMessageElement(message) {
            const div = document.createElement('div');
            div.className = `message ${message.sender_id === window.currentUserId ? 'own' : 'other'}`;
            div.innerHTML = `
                <div class="message-content">
                    <div class="message-text">${message.content}</div>
                    <div class="message-time">${this.formatTime(message.timestamp)}</div>
                </div>
            `;
            return div;
        },
        
        // Mark notification as read
        markNotificationRead(notificationId) {
            const notification = this.notifications.find(n => n.id === notificationId);
            if (notification && !notification.read) {
                notification.read = true;
                this.unreadCount--;
                this.updateNotificationBadge();
                
                // Send to server
                fetch(`/api/v1/notifications/${notificationId}/read/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                        'Content-Type': 'application/json'
                    }
                }).catch(error => console.warn('Failed to mark notification as read:', error));
            }
        },
        
        // Clear all notifications
        clearAllNotifications() {
            this.notifications = [];
            this.unreadCount = 0;
            this.updateNotificationBadge();
        },
        
        // Format time helper
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
    
    // Additional Alpine.js components for advanced features
    console.log('Setting up advanced Alpine components');
    
    // Enhanced components that depend on the store
    Alpine.data('chatBox', () => ({
        messages: [],
        newMessage: '',
        
        init() {
            this.messages = this.$store.realtime.messages;
            
            // Watch for new messages
            this.$watch('$store.realtime.messages', () => {
                this.messages = this.$store.realtime.messages;
                this.scrollToBottom();
            });
        },
        
        sendMessage() {
            if (this.newMessage.trim()) {
                // Send via WebSocket or API
                if (this.$store.realtime.socket && this.$store.realtime.socket.readyState === WebSocket.OPEN) {
                    this.$store.realtime.socket.send(JSON.stringify({
                        type: 'message',
                        payload: {
                            content: this.newMessage,
                            timestamp: new Date().toISOString()
                        }
                    }));
                }
                
                this.newMessage = '';
            }
        },
        
        scrollToBottom() {
            this.$nextTick(() => {
                const container = this.$el.querySelector('.messages-container');
                if (container) {
                    container.scrollTop = container.scrollHeight;
                }
            });
        }
    }));
    
    Alpine.data('userPresenceIndicator', (userId) => ({
        userId: userId,
        
        init() {
            // Watch for presence updates
            this.$watch('$store.realtime.onlineUsers', () => {
                this.updateStatus();
            });
        },
        
        get isOnline() {
            return this.$store.realtime.onlineUsers.has(this.userId);
        },
        
        updateStatus() {
            const indicator = this.$el.querySelector('.presence-dot');
            if (indicator) {
                indicator.classList.toggle('online', this.isOnline);
                indicator.classList.toggle('offline', !this.isOnline);
            }
        }
    }));
});

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
    
    // Initialize real-time features after Alpine is loaded
    setTimeout(() => {
        if (window.Alpine && Alpine.store('realtime')) {
            console.log('Real-time features ready');
            // Store is already initialized in alpine-components.js
            // No .init() needed since it's not a function
        }
    }, 200);
});

// CSS for real-time updates
const realtimeCSS = `
.updated {
    animation: pulse-update 2s ease;
}

@keyframes pulse-update {
    0% { transform: scale(1); }
    50% { transform: scale(1.02); box-shadow: 0 0 20px rgba(13, 110, 253, 0.3); }
    100% { transform: scale(1); }
}

.notification-badge {
    background: #dc3545;
    color: white;
    border-radius: 50%;
    font-size: 0.75rem;
    font-weight: bold;
    min-width: 18px;
    height: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    top: -8px;
    right: -8px;
}

.presence-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    position: absolute;
    bottom: 0;
    right: 0;
    border: 2px solid white;
}

.presence-dot.online {
    background: #28a745;
}

.presence-dot.offline {
    background: #6c757d;
}

.connection-status {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1050;
    transition: all 0.3s ease;
}

.connection-status.connected {
    background: #d1e7dd;
    color: #0f5132;
}

.connection-status.disconnected {
    background: #f8d7da;
    color: #721c24;
}

.connection-status.reconnecting {
    background: #fff3cd;
    color: #856404;
}

.message.own {
    text-align: right;
}

.message.other {
    text-align: left;
}

.message-content {
    display: inline-block;
    max-width: 70%;
    padding: 8px 12px;
    border-radius: 18px;
    margin: 2px 0;
}

.message.own .message-content {
    background: #0d6efd;
    color: white;
}

.message.other .message-content {
    background: #f8f9fa;
    color: #333;
}

.message-time {
    font-size: 0.75rem;
    opacity: 0.7;
    margin-top: 4px;
}
`;

// Add CSS to document
const style = document.createElement('style');
style.textContent = realtimeCSS;
document.head.appendChild(style);