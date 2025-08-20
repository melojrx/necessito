/**
 * AddressHelper - Integração com APIs de endereçamento
 * Funcionalidades:
 * - Busca automática por CEP
 * - Autocomplete de endereços
 * - Mapa interativo com marcador
 * - Geolocalização
 */

class AddressHelper {
    constructor(options = {}) {
        this.options = {
            // URLs das APIs
            cepUrl: '/api/django/address/cep/',
            searchUrl: '/api/django/address/search/',
            geocodeUrl: '/api/django/address/geocode/',
            
            // Elementos do formulário
            cepField: options.cepField || '[name="cep_servico"]',
            endereco: options.endereco || '[name="endereco_servico"]',
            numero: options.numero || '[name="numero_servico"]', 
            complemento: options.complemento || '[name="complemento_servico"]',
            bairro: options.bairro || '[name="bairro_servico"]',
            cidade: options.cidade || '[name="cidade_servico"]',
            estado: options.estado || '[name="estado_servico"]',
            useUserAddressCheckbox: options.useUserAddressCheckbox || '[name="usar_endereco_usuario"]',
            
            // Campos hidden para coordenadas
            latField: options.latField || '[name="lat_servico"]',
            lonField: options.lonField || '[name="lon_servico"]',
            
            // Elementos do mapa
            mapContainer: options.mapContainer || '#address-map',
            
            // Configurações
            debounceTime: options.debounceTime || 500,
            autocompleteMinLength: options.autocompleteMinLength || 3,
            
            // Callbacks
            onAddressFound: options.onAddressFound || null,
            onAddressNotFound: options.onAddressNotFound || null,
            onCoordinatesFound: options.onCoordinatesFound || null,
            
            ...options
        };
        
        this.map = null;
        this.marker = null;
        this.debounceTimer = null;
        this.autocompleteContainer = null;
        
        this.init();
    }
    
    init() {
        this.setupCEPLookup();
        this.setupAddressToggle();
        this.setupAutocomplete();
        this.setupMap();
        this.addStyles();
    }
    
    /**
     * Configura busca automática por CEP
     */
    setupCEPLookup() {
        const cepField = document.querySelector(this.options.cepField);
        if (!cepField) return;
        
        cepField.addEventListener('input', (e) => {
            let cep = e.target.value.replace(/\D/g, '');
            
            // Aplicar máscara
            if (cep.length <= 8) {
                if (cep.length > 5) {
                    cep = cep.replace(/(\d{5})(\d)/, '$1-$2');
                }
                e.target.value = cep;
            }
            
            // Buscar quando CEP estiver completo
            if (cep.replace('-', '').length === 8) {
                this.searchByCEP(cep);
            }
        });
        
        // Bloquear caracteres não numéricos
        cep.addEventListener('keypress', (e) => {
            if (!/\d/.test(e.key) && !['Backspace', 'Delete', 'Tab', 'Enter'].includes(e.key)) {
                e.preventDefault();
            }
        });
    }
    
    /**
     * Busca endereço por CEP
     */
    async searchByCEP(cep) {
        const cleanCEP = cep.replace(/\D/g, '');
        
        try {
            this.showLoading('Buscando CEP...');
            
            const response = await fetch(`${this.options.cepUrl}?cep=${cleanCEP}`);
            const result = await response.json();
            
            this.hideLoading();
            
            if (result.success) {
                this.fillAddressFields(result.data);
                this.geocodeAddress(result.data);
                
                if (this.options.onAddressFound) {
                    this.options.onAddressFound(result.data);
                }
            } else {
                this.showError(result.error || 'CEP não encontrado');
                if (this.options.onAddressNotFound) {
                    this.options.onAddressNotFound(result.error);
                }
            }
        } catch (error) {
            this.hideLoading();
            this.showError('Erro ao buscar CEP. Tente novamente.');
            console.error('Erro na busca de CEP:', error);
        }
    }
    
    /**
     * Preenche campos do formulário com dados do endereço
     */
    fillAddressFields(addressData) {
        const fields = {
            [this.options.endereco]: addressData.logradouro || '',
            [this.options.bairro]: addressData.bairro || '',
            [this.options.cidade]: addressData.cidade || '',
            [this.options.estado]: addressData.estado || ''
        };
        
        Object.entries(fields).forEach(([selector, value]) => {
            const field = document.querySelector(selector);
            if (field) {
                field.value = value;
                // Disparar evento change para frameworks como Alpine.js
                field.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
    }
    
    /**
     * Configura toggle entre endereço do usuário e endereço personalizado
     */
    setupAddressToggle() {
        const checkbox = document.querySelector(this.options.useUserAddressCheckbox);
        if (!checkbox) return;
        
        const addressFields = [
            this.options.cepField,
            this.options.endereco,
            this.options.numero,
            this.options.complemento,
            this.options.bairro,
            this.options.cidade,
            this.options.estado
        ];
        
        const toggleFields = (disabled) => {
            addressFields.forEach(selector => {
                const field = document.querySelector(selector);
                if (field) {
                    field.disabled = disabled;
                    if (disabled) {
                        field.style.backgroundColor = '#f8f9fa';
                    } else {
                        field.style.backgroundColor = '';
                    }
                }
            });
        };
        
        // Estado inicial
        toggleFields(checkbox.checked);
        
        checkbox.addEventListener('change', (e) => {
            const useUserAddress = e.target.checked;
            toggleFields(useUserAddress);
            
            if (useUserAddress) {
                this.loadUserAddress();
            } else {
                this.clearAddressFields();
            }
        });
    }
    
    /**
     * Carrega endereço do usuário logado
     */
    async loadUserAddress() {
        try {
            const response = await fetch('/api/v1/address/user/', {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`,
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    this.fillAddressFields(result.data);
                    if (result.data.lat && result.data.lon) {
                        this.updateMapMarker(result.data.lat, result.data.lon);
                    }
                }
            }
        } catch (error) {
            console.error('Erro ao carregar endereço do usuário:', error);
        }
    }
    
    /**
     * Limpa campos de endereço
     */
    clearAddressFields() {
        const fields = [
            this.options.cepField,
            this.options.endereco,
            this.options.numero,
            this.options.complemento,
            this.options.bairro,
            this.options.cidade,
            this.options.estado
        ];
        
        fields.forEach(selector => {
            const field = document.querySelector(selector);
            if (field) {
                field.value = '';
            }
        });
        
        this.clearCoordinates();
    }
    
    /**
     * Configura autocomplete de endereços
     */
    setupAutocomplete() {
        const enderecoField = document.querySelector(this.options.endereco);
        if (!enderecoField) return;
        
        // Criar container para sugestões
        this.autocompleteContainer = document.createElement('div');
        this.autocompleteContainer.className = 'address-autocomplete-container';
        enderecoField.parentNode.style.position = 'relative';
        enderecoField.parentNode.appendChild(this.autocompleteContainer);
        
        enderecoField.addEventListener('input', (e) => {
            clearTimeout(this.debounceTimer);
            
            const query = e.target.value.trim();
            
            if (query.length < this.options.autocompleteMinLength) {
                this.hideAutocomplete();
                return;
            }
            
            this.debounceTimer = setTimeout(() => {
                this.searchAddresses(query);
            }, this.options.debounceTime);
        });
        
        // Fechar autocomplete ao clicar fora
        document.addEventListener('click', (e) => {
            if (!enderecoField.contains(e.target) && !this.autocompleteContainer.contains(e.target)) {
                this.hideAutocomplete();
            }
        });
    }
    
    /**
     * Busca endereços para autocomplete
     */
    async searchAddresses(query) {
        try {
            const response = await fetch(`${this.options.searchUrl}?q=${encodeURIComponent(query)}&limit=5`);
            const result = await response.json();
            
            if (result.success && result.data.length > 0) {
                this.showAutocomplete(result.data);
            } else {
                this.hideAutocomplete();
            }
        } catch (error) {
            console.error('Erro na busca de endereços:', error);
            this.hideAutocomplete();
        }
    }
    
    /**
     * Exibe sugestões de autocomplete
     */
    showAutocomplete(addresses) {
        const container = this.autocompleteContainer;
        container.innerHTML = '';
        
        addresses.forEach(address => {
            const item = document.createElement('div');
            item.className = 'address-autocomplete-item';
            item.innerHTML = `
                <div class="address-main">${address.road || address.display_name}</div>
                <div class="address-details">${address.neighbourhood || ''} - ${address.city}, ${address.state}</div>
            `;
            
            item.addEventListener('click', () => {
                this.selectAddress(address);
                this.hideAutocomplete();
            });
            
            container.appendChild(item);
        });
        
        container.style.display = 'block';
    }
    
    /**
     * Oculta autocomplete
     */
    hideAutocomplete() {
        if (this.autocompleteContainer) {
            this.autocompleteContainer.style.display = 'none';
        }
    }
    
    /**
     * Seleciona endereço do autocomplete
     */
    selectAddress(address) {
        // Preencher campos
        const enderecoField = document.querySelector(this.options.endereco);
        const bairroField = document.querySelector(this.options.bairro);
        const cidadeField = document.querySelector(this.options.cidade);
        const estadoField = document.querySelector(this.options.estado);
        
        if (enderecoField) enderecoField.value = address.road || '';
        if (bairroField) bairroField.value = address.neighbourhood || '';
        if (cidadeField) cidadeField.value = address.city || '';
        if (estadoField) estadoField.value = address.state || '';
        
        // Atualizar coordenadas e mapa
        this.updateCoordinates(address.lat, address.lon);
        this.updateMapMarker(address.lat, address.lon);
    }
    
    /**
     * Geocodifica endereço para obter coordenadas
     */
    async geocodeAddress(addressData) {
        try {
            const response = await fetch(this.options.geocodeUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    address: addressData.logradouro || '',
                    city: addressData.cidade || '',
                    state: addressData.estado || ''
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                const { lat, lon } = result.data;
                this.updateCoordinates(lat, lon);
                this.updateMapMarker(lat, lon);
                
                if (this.options.onCoordinatesFound) {
                    this.options.onCoordinatesFound(lat, lon);
                }
            }
        } catch (error) {
            console.error('Erro no geocoding:', error);
        }
    }
    
    /**
     * Atualiza campos de coordenadas
     */
    updateCoordinates(lat, lon) {
        const latField = document.querySelector(this.options.latField);
        const lonField = document.querySelector(this.options.lonField);
        
        if (latField) latField.value = lat;
        if (lonField) lonField.value = lon;
    }
    
    /**
     * Limpa coordenadas
     */
    clearCoordinates() {
        this.updateCoordinates('', '');
        if (this.marker && this.map) {
            this.map.removeLayer(this.marker);
            this.marker = null;
        }
    }
    
    /**
     * Configura mapa interativo
     */
    setupMap() {
        const mapContainer = document.querySelector(this.options.mapContainer);
        if (!mapContainer || !window.L) return;
        
        // Inicializar mapa centrado no Brasil
        this.map = L.map(mapContainer).setView([-14.2350, -51.9253], 4);
        
        // Adicionar camada do OpenStreetMap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
        
        // Evento de clique no mapa
        this.map.on('click', (e) => {
            const { lat, lng: lon } = e.latlng;
            this.updateCoordinates(lat, lon);
            this.updateMapMarker(lat, lon);
            this.reverseGeocode(lat, lon);
        });
    }
    
    /**
     * Atualiza marcador no mapa
     */
    updateMapMarker(lat, lon) {
        if (!this.map) return;
        
        // Remover marcador anterior
        if (this.marker) {
            this.map.removeLayer(this.marker);
        }
        
        // Adicionar novo marcador
        this.marker = L.marker([lat, lon]).addTo(this.map);
        
        // Centralizar mapa no marcador
        this.map.setView([lat, lon], 15);
    }
    
    /**
     * Geocoding reverso (coordenadas -> endereço)
     */
    async reverseGeocode(lat, lon) {
        try {
            const response = await fetch(
                `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&addressdetails=1`,
                { headers: { 'User-Agent': 'Indicai-Marketplace/1.0' }}
            );
            
            const data = await response.json();
            
            if (data && data.address) {
                const address = data.address;
                this.fillAddressFields({
                    logradouro: address.road || '',
                    bairro: address.neighbourhood || address.suburb || '',
                    cidade: address.city || address.town || address.village || '',
                    estado: address.state || '',
                });
            }
        } catch (error) {
            console.error('Erro no geocoding reverso:', error);
        }
    }
    
    /**
     * Helpers
     */
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
    
    getAuthToken() {
        // Implementar conforme seu sistema de autenticação
        return localStorage.getItem('authToken') || '';
    }
    
    showLoading(message = 'Carregando...') {
        // Implementar loading indicator
        console.log('Loading:', message);
    }
    
    hideLoading() {
        // Ocultar loading indicator
        console.log('Loading finished');
    }
    
    showError(message) {
        // Implementar exibição de erro
        console.error('Erro:', message);
        alert(message); // Substituir por toast ou modal
    }
    
    /**
     * Adiciona estilos CSS para autocomplete
     */
    addStyles() {
        if (document.getElementById('address-helper-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'address-helper-styles';
        styles.textContent = `
            .address-autocomplete-container {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                border: 1px solid #ddd;
                border-top: none;
                border-radius: 0 0 4px 4px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                z-index: 1000;
                max-height: 200px;
                overflow-y: auto;
                display: none;
            }
            
            .address-autocomplete-item {
                padding: 10px;
                cursor: pointer;
                border-bottom: 1px solid #f0f0f0;
                transition: background-color 0.2s;
            }
            
            .address-autocomplete-item:hover {
                background-color: #f8f9fa;
            }
            
            .address-autocomplete-item:last-child {
                border-bottom: none;
            }
            
            .address-main {
                font-weight: 500;
                color: #333;
                margin-bottom: 2px;
            }
            
            .address-details {
                font-size: 0.9em;
                color: #666;
            }
        `;
        
        document.head.appendChild(styles);
    }
}

// Exportar para uso global
window.AddressHelper = AddressHelper;

// Auto-inicializar em formulários com classe 'address-form'
document.addEventListener('DOMContentLoaded', function() {
    const addressForms = document.querySelectorAll('.address-form');
    addressForms.forEach(form => {
        new AddressHelper();
    });
});