/**
 * FASE 1 - Modernização do Sistema de Busca
 * Preserva funcionalidade existente e adiciona melhorias incrementais
 */

class SearchModernization {
    constructor() {
        this.autocompleteContainer = null;
        this.autocompleteInput = null;
        this.autocompleteDropdown = null;
        this.mobileDrawer = null;
        this.mobileDrawerBackdrop = null;
        this.searchForm = null;
        this.debounceTimer = null;
        this.currentRequest = null;
        this.selectedIndex = -1;
        this.autocompleteResults = [];
        
        this.init();
    }
    
    init() {
        // Aguardar DOM estar pronto
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeComponents());
        } else {
            this.initializeComponents();
        }
    }
    
    initializeComponents() {
        console.log('🚀 Search Modernization initialized');
        this.initAutocomplete();
        this.initMobileDrawer();
        this.initProgressBar();
        this.initKeyboardNavigation();
        this.initStatusFilter();
        this.preserveExistingFunctionality();
    }
    
    // ===== AUTOCOMPLETE INTELIGENTE =====
    initAutocomplete() {
        const searchInput = document.querySelector('input[name="q"]');
        if (!searchInput) return;
        
        this.createAutocompleteStructure(searchInput);
        this.bindAutocompleteEvents();
    }
    
    createAutocompleteStructure(originalInput) {
        // Criar container do autocomplete
        this.autocompleteContainer = document.createElement('div');
        this.autocompleteContainer.className = 'search-autocomplete-container';
        
        // Substituir input original
        originalInput.parentNode.insertBefore(this.autocompleteContainer, originalInput);
        this.autocompleteContainer.appendChild(originalInput);
        
        // Adicionar classes ao input
        originalInput.classList.add('search-autocomplete-input');
        this.autocompleteInput = originalInput;
        
        // Criar dropdown
        this.autocompleteDropdown = document.createElement('div');
        this.autocompleteDropdown.className = 'search-autocomplete-dropdown';
        this.autocompleteContainer.appendChild(this.autocompleteDropdown);
    }
    
    bindAutocompleteEvents() {
        // Input events
        this.autocompleteInput.addEventListener('input', (e) => {
            this.handleAutocompleteInput(e.target.value);
        });
        
        this.autocompleteInput.addEventListener('focus', () => {
            if (this.autocompleteInput.value.trim().length >= 2) {
                this.showAutocompleteDropdown();
            }
        });
        
        this.autocompleteInput.addEventListener('blur', (e) => {
            // Delay para permitir clique nos resultados
            setTimeout(() => {
                this.hideAutocompleteDropdown();
            }, 150);
        });
        
        // Keyboard navigation
        this.autocompleteInput.addEventListener('keydown', (e) => {
            this.handleAutocompleteKeydown(e);
        });
        
        // Click fora para fechar
        document.addEventListener('click', (e) => {
            if (!this.autocompleteContainer.contains(e.target)) {
                this.hideAutocompleteDropdown();
            }
        });
    }
    
    handleAutocompleteInput(value) {
        const term = value.trim();
        
        // Cancelar busca anterior
        if (this.currentRequest) {
            this.currentRequest.abort();
        }
        
        // Limpar timer anterior
        clearTimeout(this.debounceTimer);
        
        // Reset selection
        this.selectedIndex = -1;
        
        if (term.length < 2) {
            this.hideAutocompleteDropdown();
            return;
        }
        
        // Debounce para evitar muitas requisições
        this.debounceTimer = setTimeout(() => {
            this.fetchAutocompleteResults(term);
        }, 300);
    }
    
    async fetchAutocompleteResults(term) {
        try {
            // Mostrar loading
            this.showAutocompleteLoading();
            
            // Criar AbortController para cancelar se necessário
            const controller = new AbortController();
            this.currentRequest = controller;
            
            const response = await fetch(`/search/autocomplete/?term=${encodeURIComponent(term)}`, {
                signal: controller.signal
            });
            
            if (!response.ok) throw new Error('Erro na busca');
            
            const data = await response.json();
            this.renderAutocompleteResults(data.results);
            
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Erro no autocomplete:', error);
                this.showAutocompleteError();
            }
        } finally {
            this.currentRequest = null;
        }
    }
    
    showAutocompleteLoading() {
        this.autocompleteDropdown.innerHTML = `
            <div class="autocomplete-loading">
                <i class="fas fa-spinner fa-spin me-2"></i>
                Buscando sugestões...
            </div>
        `;
        this.showAutocompleteDropdown();
    }
    
    showAutocompleteError() {
        this.autocompleteDropdown.innerHTML = `
            <div class="autocomplete-no-results">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Erro ao buscar sugestões
            </div>
        `;
    }
    
    renderAutocompleteResults(groupedResults) {
        if (!groupedResults || Object.keys(groupedResults).length === 0) {
            this.autocompleteDropdown.innerHTML = `
                <div class="autocomplete-no-results">
                    <i class="fas fa-search me-2"></i>
                    Nenhuma sugestão encontrada
                </div>
            `;
            return;
        }
        
        let html = '';
        this.autocompleteResults = [];
        
        Object.entries(groupedResults).forEach(([groupName, items]) => {
            html += `<div class="autocomplete-group">`;
            html += `<h6 class="autocomplete-group-header">${groupName}</h6>`;
            
            items.forEach((item, index) => {
                const globalIndex = this.autocompleteResults.length;
                this.autocompleteResults.push(item);
                
                html += `
                    <button class="autocomplete-item" data-index="${globalIndex}">
                        <i class="autocomplete-item-icon ${item.icon}"></i>
                        <span class="autocomplete-item-text">${item.text}</span>
                    </button>
                `;
            });
            
            html += `</div>`;
        });
        
        this.autocompleteDropdown.innerHTML = html;
        
        // Bind click events
        this.autocompleteDropdown.querySelectorAll('.autocomplete-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const index = parseInt(e.currentTarget.dataset.index);
                this.selectAutocompleteItem(index);
            });
        });
        
        this.showAutocompleteDropdown();
    }
    
    handleAutocompleteKeydown(e) {
        if (!this.autocompleteDropdown.classList.contains('show')) return;
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.navigateAutocomplete(1);
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.navigateAutocomplete(-1);
                break;
            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0) {
                    this.selectAutocompleteItem(this.selectedIndex);
                }
                break;
            case 'Escape':
                this.hideAutocompleteDropdown();
                break;
        }
    }
    
    navigateAutocomplete(direction) {
        const items = this.autocompleteDropdown.querySelectorAll('.autocomplete-item');
        
        // Remove seleção anterior
        items.forEach(item => item.classList.remove('selected'));
        
        // Calcular novo índice
        this.selectedIndex += direction;
        
        if (this.selectedIndex < 0) {
            this.selectedIndex = items.length - 1;
        } else if (this.selectedIndex >= items.length) {
            this.selectedIndex = 0;
        }
        
        // Aplicar nova seleção
        if (items[this.selectedIndex]) {
            items[this.selectedIndex].classList.add('selected');
            items[this.selectedIndex].scrollIntoView({ block: 'nearest' });
        }
    }
    
    selectAutocompleteItem(index) {
        const item = this.autocompleteResults[index];
        if (!item) return;
        
        // Definir valor do input
        this.autocompleteInput.value = item.text;
        
        // Ocultar dropdown
        this.hideAutocompleteDropdown();
        
        // Submit automático ou foco no próximo campo
        // Preserva comportamento existente
        this.autocompleteInput.focus();
    }
    
    showAutocompleteDropdown() {
        this.autocompleteDropdown.classList.add('show');
    }
    
    hideAutocompleteDropdown() {
        this.autocompleteDropdown.classList.remove('show');
        this.selectedIndex = -1;
    }
    
    // ===== DRAWER MOBILE =====
    initMobileDrawer() {
        if (window.innerWidth > 768) return; // Apenas para mobile
        
        this.createMobileDrawerStructure();
        this.bindMobileDrawerEvents();
    }
    
    createMobileDrawerStructure() {
        // Criar trigger button
        const trigger = document.createElement('button');
        trigger.className = 'mobile-filters-trigger';
        trigger.innerHTML = '<i class="fas fa-filter"></i>';
        trigger.setAttribute('aria-label', 'Abrir filtros');
        document.body.appendChild(trigger);
        
        // Criar backdrop
        this.mobileDrawerBackdrop = document.createElement('div');
        this.mobileDrawerBackdrop.className = 'mobile-drawer-backdrop';
        document.body.appendChild(this.mobileDrawerBackdrop);
        
        // Criar drawer
        this.mobileDrawer = document.createElement('div');
        this.mobileDrawer.className = 'mobile-drawer';
        this.mobileDrawer.innerHTML = this.getMobileDrawerContent();
        document.body.appendChild(this.mobileDrawer);
        
        // Mover form para dentro do drawer
        this.moveFiltersToDrawer();
    }
    
    getMobileDrawerContent() {
        return `
            <div class="mobile-drawer-header">
                <h3 class="mobile-drawer-title">Filtros de Busca</h3>
                <button class="mobile-drawer-close" aria-label="Fechar">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="mobile-drawer-content">
                <!-- Conteúdo dos filtros será movido aqui -->
            </div>
            <div class="mobile-drawer-actions">
                <button type="button" class="mobile-drawer-btn mobile-drawer-btn-secondary" id="clear-filters">
                    Limpar
                </button>
                <button type="submit" class="mobile-drawer-btn mobile-drawer-btn-primary" id="apply-filters">
                    Aplicar
                </button>
            </div>
        `;
    }
    
    moveFiltersToDrawer() {
        const form = document.querySelector('form[method="get"]');
        if (!form) return;
        
        this.searchForm = form;
        const drawerContent = this.mobileDrawer.querySelector('.mobile-drawer-content');
        
        // Para mobile, usar versão simplificada do status filter
        this.createMobileStatusFilter(drawerContent);
        
        // Clonar outros elementos de filtro para o drawer
        const formElements = form.querySelectorAll('input:not([name="q"]):not([name="status"]), .form-check:not(.status-checkbox)');
        
        formElements.forEach(element => {
            const clone = element.cloneNode(true);
            
            // Adicionar wrapper para melhor styling
            const wrapper = document.createElement('div');
            wrapper.className = 'mobile-filter-section';
            
            if (element.tagName === 'INPUT') {
                const label = document.createElement('label');
                label.className = 'mobile-filter-label';
                label.textContent = element.placeholder || element.name;
                wrapper.appendChild(label);
                
                clone.className = 'mobile-filter-input';
                wrapper.appendChild(clone);
            } else {
                wrapper.appendChild(clone);
            }
            
            drawerContent.appendChild(wrapper);
        });
    }
    
    createMobileStatusFilter(drawerContent) {
        const statusSection = document.createElement('div');
        statusSection.className = 'mobile-filter-section';
        statusSection.innerHTML = `
            <label class="mobile-filter-label">Status</label>
            <div class="mobile-filter-checkboxes" id="mobileStatusOptions">
                <!-- Status checkboxes will be populated here -->
            </div>
        `;
        drawerContent.appendChild(statusSection);
        
        // Populate with status options
        const desktopStatusOptions = document.querySelectorAll('.status-filter-option');
        const mobileStatusContainer = statusSection.querySelector('#mobileStatusOptions');
        
        desktopStatusOptions.forEach(option => {
            const checkbox = option.querySelector('.status-checkbox');
            const label = option.querySelector('.status-text').textContent;
            const icon = option.querySelector('.status-icon i').outerHTML;
            
            const mobileOption = document.createElement('div');
            mobileOption.className = 'mobile-filter-checkbox';
            mobileOption.innerHTML = `
                <input type="checkbox" name="status" value="${checkbox.value}" ${checkbox.checked ? 'checked' : ''} id="mobile_${checkbox.value}">
                <label for="mobile_${checkbox.value}" class="d-flex align-items-center gap-2">
                    ${icon}
                    <span>${label}</span>
                </label>
            `;
            
            mobileStatusContainer.appendChild(mobileOption);
        });
    }
    
    bindMobileDrawerEvents() {
        const trigger = document.querySelector('.mobile-filters-trigger');
        const close = this.mobileDrawer.querySelector('.mobile-drawer-close');
        const applyBtn = this.mobileDrawer.querySelector('#apply-filters');
        const clearBtn = this.mobileDrawer.querySelector('#clear-filters');
        
        // Abrir drawer
        trigger.addEventListener('click', () => this.openMobileDrawer());
        
        // Fechar drawer
        close.addEventListener('click', () => this.closeMobileDrawer());
        this.mobileDrawerBackdrop.addEventListener('click', () => this.closeMobileDrawer());
        
        // Aplicar filtros
        applyBtn.addEventListener('click', () => {
            this.applyMobileFilters();
            this.closeMobileDrawer();
        });
        
        // Limpar filtros
        clearBtn.addEventListener('click', () => {
            this.clearMobileFilters();
        });
        
        // Touch gestures para fechar
        this.initTouchGestures();
        
        // Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.mobileDrawer.classList.contains('show')) {
                this.closeMobileDrawer();
            }
        });
    }
    
    openMobileDrawer() {
        // Sync valores do form principal para o drawer
        this.syncFiltersToDrawer();
        
        // Mostrar drawer
        this.mobileDrawerBackdrop.classList.add('show');
        this.mobileDrawer.classList.add('show');
        
        // Trigger toggle
        document.querySelector('.mobile-filters-trigger').classList.add('active');
        
        // Prevenir scroll do body
        document.body.style.overflow = 'hidden';
    }
    
    closeMobileDrawer() {
        this.mobileDrawerBackdrop.classList.remove('show');
        this.mobileDrawer.classList.remove('show');
        document.querySelector('.mobile-filters-trigger').classList.remove('active');
        
        // Restaurar scroll
        document.body.style.overflow = '';
    }
    
    syncFiltersToDrawer() {
        const formInputs = this.searchForm.querySelectorAll('input, select');
        const drawerInputs = this.mobileDrawer.querySelectorAll('input, select');
        
        formInputs.forEach((input, index) => {
            const drawerInput = drawerInputs[index];
            if (drawerInput) {
                if (input.type === 'checkbox' || input.type === 'radio') {
                    drawerInput.checked = input.checked;
                } else {
                    drawerInput.value = input.value;
                }
            }
        });
    }
    
    applyMobileFilters() {
        // Sync valores do drawer para o form principal
        const formInputs = this.searchForm.querySelectorAll('input, select');
        const drawerInputs = this.mobileDrawer.querySelectorAll('input, select');
        
        drawerInputs.forEach((drawerInput, index) => {
            const formInput = formInputs[index];
            if (formInput) {
                if (drawerInput.type === 'checkbox' || drawerInput.type === 'radio') {
                    formInput.checked = drawerInput.checked;
                } else {
                    formInput.value = drawerInput.value;
                }
            }
        });
        
        // Submit form
        this.showProgressBar();
        this.searchForm.submit();
    }
    
    clearMobileFilters() {
        const inputs = this.mobileDrawer.querySelectorAll('input:not([name="q"]):not([name="state"])');
        inputs.forEach(input => {
            if (input.type === 'checkbox' || input.type === 'radio') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });
    }
    
    initTouchGestures() {
        let startX = 0;
        let currentX = 0;
        let isDragging = false;
        
        this.mobileDrawer.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            isDragging = true;
        });
        
        this.mobileDrawer.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            
            currentX = e.touches[0].clientX;
            const diffX = currentX - startX;
            
            // Apenas para direita (fechar)
            if (diffX > 0) {
                const opacity = Math.max(0, 1 - (diffX / 200));
                this.mobileDrawer.style.transform = `translateX(${diffX}px)`;
                this.mobileDrawerBackdrop.style.opacity = opacity;
            }
        });
        
        this.mobileDrawer.addEventListener('touchend', () => {
            if (!isDragging) return;
            
            const diffX = currentX - startX;
            
            if (diffX > 100) {
                this.closeMobileDrawer();
            } else {
                // Voltar posição original
                this.mobileDrawer.style.transform = '';
                this.mobileDrawerBackdrop.style.opacity = '';
            }
            
            isDragging = false;
        });
    }
    
    // ===== PROGRESS BAR =====
    initProgressBar() {
        // Criar progress bar
        this.progressBar = document.createElement('div');
        this.progressBar.className = 'search-progress-bar';
        document.body.appendChild(this.progressBar);
        
        // Intercept form submits para mostrar progress
        const forms = document.querySelectorAll('form[method="get"]');
        forms.forEach(form => {
            form.addEventListener('submit', () => {
                this.showProgressBar();
            });
        });
    }
    
    showProgressBar() {
        this.progressBar.classList.add('show');
        this.progressBar.style.width = '30%';
        
        // Simular progresso
        setTimeout(() => {
            this.progressBar.style.width = '60%';
        }, 200);
        
        setTimeout(() => {
            this.progressBar.style.width = '90%';
        }, 500);
        
        // Auto-hide após 2 segundos
        setTimeout(() => {
            this.hideProgressBar();
        }, 2000);
    }
    
    hideProgressBar() {
        this.progressBar.style.width = '100%';
        setTimeout(() => {
            this.progressBar.classList.remove('show');
            this.progressBar.style.width = '0%';
        }, 300);
    }
    
    // ===== NAVEGAÇÃO POR TECLADO =====
    initKeyboardNavigation() {
        // Adicionar navegação por teclado nos cards de resultado
        const cards = document.querySelectorAll('.listing-card');
        cards.forEach((card, index) => {
            card.setAttribute('tabindex', '0');
            
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    card.click();
                }
            });
        });
    }
    
    // ===== STATUS FILTER INTEGRATION =====
    initStatusFilter() {
        // Integração com o filtro de status customizado
        const statusDropdown = document.querySelector('.status-filter-dropdown-wrapper');
        if (!statusDropdown) return;
        
        // Adicionar melhorias de UX ao filtro de status
        this.enhanceStatusFilterUX();
    }
    
    enhanceStatusFilterUX() {
        // Auto-submit quando status é alterado (opcional)
        const statusCheckboxes = document.querySelectorAll('.status-checkbox');
        statusCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                // Adicionar pequeno delay para melhor UX
                clearTimeout(this.statusSubmitTimer);
                this.statusSubmitTimer = setTimeout(() => {
                    // Auto-submit pode ser habilitado aqui se desejado
                    // this.searchForm?.submit();
                }, 1000);
            });
        });
        
        // Melhorar acessibilidade
        const statusToggle = document.getElementById('statusDropdownToggle');
        if (statusToggle) {
            statusToggle.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    statusToggle.click();
                }
            });
        }
    }
    
    // ===== PRESERVAR FUNCIONALIDADE EXISTENTE =====
    preserveExistingFunctionality() {
        // Garantir que funcionalidades existentes continuem funcionando
        
        // Geolocalização existente
        const existingGeoBtn = document.getElementById('btn-localizacao');
        if (existingGeoBtn && window.usarLocalizacaoAtual) {
            // Funcionalidade já existe, apenas melhorar UX
            existingGeoBtn.addEventListener('click', () => {
                this.showProgressBar();
            });
        }
        
        // Slider de raio existente
        const existingSlider = document.getElementById('sliderRaio');
        if (existingSlider) {
            existingSlider.addEventListener('input', () => {
                // Adicionar feedback visual
                existingSlider.style.background = `linear-gradient(to right, #007bff 0%, #007bff ${(existingSlider.value / existingSlider.max) * 100}%, #ddd ${(existingSlider.value / existingSlider.max) * 100}%, #ddd 100%)`;
            });
        }
        
        // Pagination existente
        const paginationLinks = document.querySelectorAll('.pagination a');
        paginationLinks.forEach(link => {
            link.addEventListener('click', () => {
                this.showProgressBar();
            });
        });
    }
}

// Inicializar quando o script for carregado
new SearchModernization();