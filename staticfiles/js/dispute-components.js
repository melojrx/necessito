/**
 * INDICAI DISPUTE SYSTEM - COMPONENTES REUTILIZÁVEIS
 * Sistema moderno e acessível para gerenciamento de disputas
 * 
 * Funcionalidades:
 * - Validação de formulários
 * - Notificações em tempo real
 * - Upload de arquivos com drag & drop
 * - Timers e contadores
 * - Animações e transições
 * - Acessibilidade (WCAG 2.1)
 * - Performance otimizada
 */

class DisputeComponents {
    constructor() {
        this.init();
    }

    /**
     * Inicialização dos componentes
     */
    init() {
        this.setupEventListeners();
        this.initializeNotifications();
        this.setupAccessibility();
        this.loadSavedDrafts();
    }

    /**
     * VALIDAÇÃO DE FORMULÁRIOS
     */
    FormValidator = {
        /**
         * Valida formulário de criação de disputa
         * @param {HTMLFormElement} form - Formulário a ser validado
         * @returns {Object} Resultado da validação
         */
        validateDisputeForm(form) {
            const motivo = form.querySelector('#id_motivo');
            const arquivo = form.querySelector('#id_arquivo_evidencia');
            const errors = [];
            let isValid = true;

            // Validar motivo
            if (motivo) {
                const text = motivo.value.trim();
                
                if (text.length < 50) {
                    errors.push({
                        field: 'motivo',
                        message: 'Descreva o problema com mais detalhes (mínimo 50 caracteres)',
                        severity: 'error'
                    });
                    isValid = false;
                } else if (text.length > 2000) {
                    errors.push({
                        field: 'motivo',
                        message: 'Descrição muito longa (máximo 2000 caracteres)',
                        severity: 'error'
                    });
                    isValid = false;
                }

                // Verificar qualidade do texto
                if (text.length >= 50 && this.checkTextQuality(text)) {
                    errors.push({
                        field: 'motivo',
                        message: 'Descrição muito detalhada - ótimo para análise!',
                        severity: 'success'
                    });
                }
            }

            // Validar arquivo se enviado
            if (arquivo && arquivo.files.length > 0) {
                const file = arquivo.files[0];
                const validationResult = this.validateFile(file);
                
                if (!validationResult.isValid) {
                    errors.push({
                        field: 'arquivo',
                        message: validationResult.message,
                        severity: 'error'
                    });
                    isValid = false;
                }
            }

            return {
                isValid,
                errors,
                suggestions: this.generateSuggestions(form)
            };
        },

        /**
         * Valida arquivo de evidência
         * @param {File} file - Arquivo a ser validado
         * @returns {Object} Resultado da validação
         */
        validateFile(file) {
            const maxSize = 10 * 1024 * 1024; // 10MB
            const allowedTypes = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'image/jpeg',
                'image/png',
                'text/plain'
            ];

            if (file.size > maxSize) {
                return {
                    isValid: false,
                    message: `Arquivo muito grande. Tamanho máximo: ${this.formatFileSize(maxSize)}`
                };
            }

            if (!allowedTypes.includes(file.type)) {
                return {
                    isValid: false,
                    message: 'Tipo de arquivo não permitido. Use PDF, Word, JPEG, PNG ou TXT'
                };
            }

            return {
                isValid: true,
                message: 'Arquivo válido'
            };
        },

        /**
         * Verifica qualidade do texto
         * @param {string} text - Texto a ser analisado
         * @returns {boolean} Se o texto é de boa qualidade
         */
        checkTextQuality(text) {
            const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
            const words = text.split(/\s+/).filter(w => w.length > 0);
            
            return sentences.length >= 3 && words.length >= 100;
        },

        /**
         * Gera sugestões para melhoria do formulário
         * @param {HTMLFormElement} form - Formulário analisado
         * @returns {Array} Lista de sugestões
         */
        generateSuggestions(form) {
            const suggestions = [];
            const motivo = form.querySelector('#id_motivo');
            const arquivo = form.querySelector('#id_arquivo_evidencia');

            if (motivo && motivo.value.trim().length > 50 && motivo.value.trim().length < 150) {
                suggestions.push('Considere adicionar mais detalhes como datas, valores ou printscreens para facilitar nossa análise.');
            }

            if (!arquivo || arquivo.files.length === 0) {
                suggestions.push('Anexar comprovantes (prints, e-mails, fotos) pode acelerar a resolução da disputa.');
            }

            return suggestions;
        },

        /**
         * Formata tamanho de arquivo
         * @param {number} bytes - Tamanho em bytes
         * @returns {string} Tamanho formatado
         */
        formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
    };

    /**
     * SISTEMA DE UPLOAD DE ARQUIVOS
     */
    FileUpload = {
        /**
         * Inicializa drag & drop para upload
         * @param {HTMLElement} uploadArea - Área de upload
         * @param {HTMLInputElement} fileInput - Input de arquivo
         * @param {HTMLElement} previewArea - Área de preview
         */
        initializeDragAndDrop(uploadArea, fileInput, previewArea) {
            if (!uploadArea || !fileInput) return;

            // Eventos de drag & drop
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, this.preventDefaults, false);
                document.body.addEventListener(eventName, this.preventDefaults, false);
            });

            ['dragenter', 'dragover'].forEach(eventName => {
                uploadArea.addEventListener(eventName, () => {
                    uploadArea.classList.add('dragover');
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, () => {
                    uploadArea.classList.remove('dragover');
                }, false);
            });

            uploadArea.addEventListener('drop', (e) => {
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFile(files[0], fileInput, previewArea);
                }
            }, false);

            // Click para upload
            uploadArea.addEventListener('click', () => {
                fileInput.click();
            });

            // Change do input
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleFile(e.target.files[0], fileInput, previewArea);
                }
            });
        },

        /**
         * Previne comportamentos padrão
         * @param {Event} e - Evento
         */
        preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        },

        /**
         * Processa arquivo selecionado
         * @param {File} file - Arquivo selecionado
         * @param {HTMLInputElement} fileInput - Input de arquivo
         * @param {HTMLElement} previewArea - Área de preview
         */
        handleFile(file, fileInput, previewArea) {
            const validation = disputeComponents.FormValidator.validateFile(file);
            
            if (!validation.isValid) {
                this.showError(validation.message, previewArea);
                fileInput.value = '';
                return;
            }

            this.showPreview(file, previewArea);
            
            // Simular seleção no input
            const dt = new DataTransfer();
            dt.items.add(file);
            fileInput.files = dt.files;
        },

        /**
         * Mostra preview do arquivo
         * @param {File} file - Arquivo
         * @param {HTMLElement} previewArea - Área de preview
         */
        showPreview(file, previewArea) {
            if (!previewArea) return;

            const icon = this.getFileIcon(file.type);
            const size = disputeComponents.FormValidator.formatFileSize(file.size);

            previewArea.innerHTML = `
                <div class="file-preview-content">
                    <div class="file-info">
                        <i class="${icon} fa-2x me-3"></i>
                        <div>
                            <div class="file-name">${file.name}</div>
                            <div class="file-size text-muted">${size}</div>
                        </div>
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-danger remove-file">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;

            previewArea.style.display = 'block';
            this.hideError(previewArea);

            // Botão remover
            const removeBtn = previewArea.querySelector('.remove-file');
            if (removeBtn) {
                removeBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.clearFile(previewArea);
                });
            }
        },

        /**
         * Mostra erro de arquivo
         * @param {string} message - Mensagem de erro
         * @param {HTMLElement} container - Container
         */
        showError(message, container) {
            const errorDiv = container.parentNode.querySelector('.file-error') || 
                           this.createErrorElement(container.parentNode);
            
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        },

        /**
         * Esconde erro de arquivo
         * @param {HTMLElement} container - Container
         */
        hideError(container) {
            const errorDiv = container.parentNode.querySelector('.file-error');
            if (errorDiv) {
                errorDiv.style.display = 'none';
            }
        },

        /**
         * Cria elemento de erro
         * @param {HTMLElement} parent - Elemento pai
         * @returns {HTMLElement} Elemento de erro
         */
        createErrorElement(parent) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'file-error mt-2 text-danger';
            errorDiv.style.display = 'none';
            parent.appendChild(errorDiv);
            return errorDiv;
        },

        /**
         * Limpa arquivo selecionado
         * @param {HTMLElement} previewArea - Área de preview
         */
        clearFile(previewArea) {
            previewArea.style.display = 'none';
            previewArea.innerHTML = '';
            
            // Limpar input
            const fileInput = document.querySelector('#id_arquivo_evidencia');
            if (fileInput) {
                fileInput.value = '';
            }
        },

        /**
         * Retorna ícone baseado no tipo de arquivo
         * @param {string} mimeType - Tipo MIME do arquivo
         * @returns {string} Classe do ícone
         */
        getFileIcon(mimeType) {
            const icons = {
                'application/pdf': 'fas fa-file-pdf text-danger',
                'application/msword': 'fas fa-file-word text-primary',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'fas fa-file-word text-primary',
                'image/jpeg': 'fas fa-file-image text-success',
                'image/png': 'fas fa-file-image text-success',
                'text/plain': 'fas fa-file-alt text-muted'
            };

            return icons[mimeType] || 'fas fa-file text-muted';
        }
    };

    /**
     * SISTEMA DE NOTIFICAÇÕES
     */
    NotificationSystem = {
        /**
         * Inicializa sistema de notificações
         */
        init() {
            // Solicitar permissão para notificações
            if ('Notification' in window && Notification.permission === 'default') {
                Notification.requestPermission();
            }

            // Criar container de toasts se não existir
            this.createToastContainer();
        },

        /**
         * Cria container de toasts
         */
        createToastContainer() {
            if (document.getElementById('toast-container')) return;

            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        },

        /**
         * Mostra toast notification
         * @param {string} message - Mensagem
         * @param {string} type - Tipo (success, error, warning, info)
         * @param {number} duration - Duração em ms
         */
        showToast(message, type = 'info', duration = 5000) {
            const container = document.getElementById('toast-container');
            if (!container) return;

            const toastId = `toast-${Date.now()}`;
            const icons = {
                success: 'fas fa-check-circle',
                error: 'fas fa-exclamation-circle',
                warning: 'fas fa-exclamation-triangle',
                info: 'fas fa-info-circle'
            };

            const colors = {
                success: 'text-bg-success',
                error: 'text-bg-danger',
                warning: 'text-bg-warning',
                info: 'text-bg-primary'
            };

            const toast = document.createElement('div');
            toast.id = toastId;
            toast.className = `toast ${colors[type]} border-0`;
            toast.setAttribute('role', 'alert');
            toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body d-flex align-items-center">
                        <i class="${icons[type]} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                            data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            `;

            container.appendChild(toast);

            // Inicializar toast do Bootstrap
            const bsToast = new bootstrap.Toast(toast, {
                autohide: true,
                delay: duration
            });

            bsToast.show();

            // Remover após esconder
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        },

        /**
         * Mostra notificação do navegador
         * @param {string} title - Título
         * @param {string} body - Corpo da mensagem
         * @param {string} icon - URL do ícone
         */
        showNotification(title, body, icon = '/static/img/logo.png') {
            if (Notification.permission === 'granted') {
                const notification = new Notification(title, {
                    body,
                    icon,
                    badge: '/static/img/favicon.ico'
                });

                // Fechar automaticamente após 5 segundos
                setTimeout(() => notification.close(), 5000);

                return notification;
            }
        }
    };

    /**
     * TIMERS E CONTADORES
     */
    TimerManager = {
        timers: new Map(),

        /**
         * Cria um timer
         * @param {string} id - ID do timer
         * @param {Date} startDate - Data de início
         * @param {HTMLElement} display - Elemento para exibir
         * @param {Function} formatter - Função de formatação
         */
        createTimer(id, startDate, display, formatter = this.defaultFormatter) {
            if (this.timers.has(id)) {
                clearInterval(this.timers.get(id));
            }

            const updateTimer = () => {
                const now = new Date();
                const diff = now - startDate;
                
                if (display) {
                    display.textContent = formatter(diff);
                }
            };

            updateTimer(); // Primeira atualização
            const interval = setInterval(updateTimer, 60000); // Atualizar a cada minuto
            this.timers.set(id, interval);
        },

        /**
         * Formatador padrão para timer
         * @param {number} milliseconds - Milissegundos
         * @returns {string} Tempo formatado
         */
        defaultFormatter(milliseconds) {
            const days = Math.floor(milliseconds / (1000 * 60 * 60 * 24));
            const hours = Math.floor((milliseconds % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((milliseconds % (1000 * 60 * 60)) / (1000 * 60));
            
            return `${days}d ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
        },

        /**
         * Remove timer
         * @param {string} id - ID do timer
         */
        removeTimer(id) {
            if (this.timers.has(id)) {
                clearInterval(this.timers.get(id));
                this.timers.delete(id);
            }
        },

        /**
         * Remove todos os timers
         */
        clearAllTimers() {
            this.timers.forEach((interval) => clearInterval(interval));
            this.timers.clear();
        }
    };

    /**
     * SISTEMA DE DRAFTS (RASCUNHOS)
     */
    DraftManager = {
        /**
         * Salva draft
         * @param {string} key - Chave única
         * @param {Object} data - Dados para salvar
         */
        saveDraft(key, data) {
            try {
                const draft = {
                    data,
                    timestamp: Date.now(),
                    version: '1.0'
                };
                localStorage.setItem(`draft_${key}`, JSON.stringify(draft));
                return true;
            } catch (error) {
                console.error('Erro ao salvar draft:', error);
                return false;
            }
        },

        /**
         * Carrega draft
         * @param {string} key - Chave única
         * @returns {Object|null} Dados salvos ou null
         */
        loadDraft(key) {
            try {
                const draftStr = localStorage.getItem(`draft_${key}`);
                if (!draftStr) return null;

                const draft = JSON.parse(draftStr);
                
                // Verificar se o draft não é muito antigo (7 dias)
                const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 dias em ms
                if (Date.now() - draft.timestamp > maxAge) {
                    this.removeDraft(key);
                    return null;
                }

                return draft.data;
            } catch (error) {
                console.error('Erro ao carregar draft:', error);
                return null;
            }
        },

        /**
         * Remove draft
         * @param {string} key - Chave única
         */
        removeDraft(key) {
            try {
                localStorage.removeItem(`draft_${key}`);
                return true;
            } catch (error) {
                console.error('Erro ao remover draft:', error);
                return false;
            }
        },

        /**
         * Lista todos os drafts
         * @returns {Array} Lista de drafts
         */
        listDrafts() {
            const drafts = [];
            try {
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    if (key && key.startsWith('draft_')) {
                        const draftStr = localStorage.getItem(key);
                        const draft = JSON.parse(draftStr);
                        drafts.push({
                            key: key.replace('draft_', ''),
                            timestamp: draft.timestamp,
                            data: draft.data
                        });
                    }
                }
            } catch (error) {
                console.error('Erro ao listar drafts:', error);
            }
            return drafts.sort((a, b) => b.timestamp - a.timestamp);
        }
    };

    /**
     * SETUP INICIAL
     */
    setupEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeComponents();
        });
    }

    /**
     * Inicializa componentes na página
     */
    initializeComponents() {
        // Auto-inicializar upload de arquivos
        const uploadArea = document.querySelector('.file-upload-area');
        const fileInput = document.querySelector('#id_arquivo_evidencia');
        const previewArea = document.querySelector('#filePreview');
        
        if (uploadArea && fileInput) {
            this.FileUpload.initializeDragAndDrop(uploadArea, fileInput, previewArea);
        }

        // Auto-inicializar timers
        this.initializeTimers();

        // Auto-inicializar validação de formulários
        this.initializeFormValidation();
    }

    /**
     * Inicializa timers na página
     */
    initializeTimers() {
        const timerElements = document.querySelectorAll('[data-timer]');
        timerElements.forEach(element => {
            const startDate = new Date(element.dataset.timerStart);
            const timerId = element.dataset.timer;
            
            if (!isNaN(startDate.getTime())) {
                this.TimerManager.createTimer(timerId, startDate, element);
            }
        });
    }

    /**
     * Inicializa validação de formulários
     */
    initializeFormValidation() {
        const disputeForms = document.querySelectorAll('form[id*="dispute"], form[id*="resolv"]');
        disputeForms.forEach(form => {
            this.setupFormValidation(form);
        });
    }

    /**
     * Configura validação para um formulário
     * @param {HTMLFormElement} form - Formulário
     */
    setupFormValidation(form) {
        const motivoField = form.querySelector('#id_motivo, #id_resolucao');
        if (motivoField) {
            // Validação em tempo real
            let validationTimeout;
            motivoField.addEventListener('input', () => {
                clearTimeout(validationTimeout);
                validationTimeout = setTimeout(() => {
                    const validation = this.FormValidator.validateDisputeForm(form);
                    this.displayValidationResults(form, validation);
                }, 500);
            });
        }

        // Validação no submit
        form.addEventListener('submit', (e) => {
            const validation = this.FormValidator.validateDisputeForm(form);
            
            if (!validation.isValid) {
                e.preventDefault();
                this.displayValidationResults(form, validation);
                this.NotificationSystem.showToast('Por favor, corrija os erros no formulário', 'error');
            }
        });
    }

    /**
     * Exibe resultados da validação
     * @param {HTMLFormElement} form - Formulário
     * @param {Object} validation - Resultado da validação
     */
    displayValidationResults(form, validation) {
        // Limpar validações anteriores
        form.querySelectorAll('.is-invalid, .is-valid').forEach(el => {
            el.classList.remove('is-invalid', 'is-valid');
        });

        form.querySelectorAll('.invalid-feedback, .valid-feedback').forEach(el => {
            el.remove();
        });

        // Aplicar nova validação
        validation.errors.forEach(error => {
            const field = form.querySelector(`#id_${error.field}`);
            if (field) {
                const className = error.severity === 'error' ? 'is-invalid' : 'is-valid';
                const feedbackClass = error.severity === 'error' ? 'invalid-feedback' : 'valid-feedback';
                
                field.classList.add(className);
                
                const feedback = document.createElement('div');
                feedback.className = feedbackClass;
                feedback.textContent = error.message;
                field.parentNode.appendChild(feedback);
            }
        });
    }

    /**
     * Inicializa sistema de notificações
     */
    initializeNotifications() {
        this.NotificationSystem.init();
    }

    /**
     * Configura acessibilidade
     */
    setupAccessibility() {
        // Adicionar navegação por teclado
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                // Fechar modais com ESC
                const openModal = document.querySelector('.modal.show');
                if (openModal) {
                    const modal = bootstrap.Modal.getInstance(openModal);
                    if (modal) modal.hide();
                }
            }
        });

        // Melhorar foco visual
        const style = document.createElement('style');
        style.textContent = `
            .btn:focus, .form-control:focus, .form-select:focus {
                outline: 3px solid rgba(13, 110, 253, 0.5);
                outline-offset: 2px;
            }
            
            @media (prefers-reduced-motion: reduce) {
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Carrega drafts salvos
     */
    loadSavedDrafts() {
        // Verificar se há drafts para a página atual
        const currentPage = window.location.pathname;
        
        if (currentPage.includes('disputa_create') || currentPage.includes('disputa_resolver')) {
            const pageId = currentPage.split('/').pop();
            const draft = this.DraftManager.loadDraft(pageId);
            
            if (draft) {
                this.loadDraftIntoForm(draft);
                this.NotificationSystem.showToast('Rascunho anterior carregado', 'info');
            }
        }
    }

    /**
     * Carrega draft no formulário
     * @param {Object} draft - Dados do draft
     */
    loadDraftIntoForm(draft) {
        Object.keys(draft).forEach(key => {
            const field = document.querySelector(`#id_${key}`);
            if (field && draft[key]) {
                field.value = draft[key];
                
                // Trigger eventos para validação
                field.dispatchEvent(new Event('input', { bubbles: true }));
            }
        });
    }

    /**
     * MÉTODOS PÚBLICOS PARA USO EXTERNO
     */

    /**
     * Salva draft automaticamente
     * @param {HTMLFormElement} form - Formulário
     * @param {string} key - Chave única
     */
    autoSaveDraft(form, key) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        return this.DraftManager.saveDraft(key, data);
    }

    /**
     * Mostra confirmação personalizada
     * @param {string} message - Mensagem
     * @param {Function} onConfirm - Callback de confirmação
     * @param {Function} onCancel - Callback de cancelamento
     */
    showConfirmation(message, onConfirm, onCancel = null) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-question-circle me-2 text-warning"></i>
                            Confirmação
                        </h5>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-action="cancel">
                            Cancelar
                        </button>
                        <button type="button" class="btn btn-primary" data-action="confirm">
                            Confirmar
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Event listeners
        modal.addEventListener('click', (e) => {
            if (e.target.dataset.action === 'confirm') {
                bsModal.hide();
                if (onConfirm) onConfirm();
            } else if (e.target.dataset.action === 'cancel') {
                bsModal.hide();
                if (onCancel) onCancel();
            }
        });

        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    /**
     * Cleanup ao sair da página
     */
    cleanup() {
        this.TimerManager.clearAllTimers();
    }
}

// Inicializar componentes globalmente
const disputeComponents = new DisputeComponents();

// Cleanup ao sair da página
window.addEventListener('beforeunload', () => {
    disputeComponents.cleanup();
});

// Disponibilizar globalmente
window.DisputeComponents = DisputeComponents;
window.disputeComponents = disputeComponents;

// Export para uso em módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DisputeComponents;
}