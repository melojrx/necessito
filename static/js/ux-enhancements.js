/**
 * ========================================
 * UX ENHANCEMENTS - NECESSITO PLATFORM
 * ========================================
 */

// Configurações globais
const UX_CONFIG = {
    masks: {
        phone: "(00) 00000-0000",
        cep: "00000-000",
        cpf: "000.000.000-00",
        cnpj: "00.000.000/0000-00",
        currency: "000.000.000,00",
        date: "00/00/0000",
        time: "00:00"
    },
    validation: {
        debounceTime: 300,
        showSuccessIcon: true,
        showErrorIcon: true
    },
    animations: {
        duration: 300,
        easing: 'ease-out'
    }
};

/**
 * ===== SISTEMA DE MÁSCARAS DE INPUT =====
 */
class InputMaskManager {
    constructor() {
        this.initMasks();
    }

    initMasks() {
        // Aplicar máscaras quando o documento estiver pronto
        $(document).ready(() => {
            this.applyMasks();
        });
    }

    applyMasks() {
        // Telefone
        $('input[name*="telefone"], input[id*="telefone"], input[type="tel"]').mask(UX_CONFIG.masks.phone, {
            placeholder: "(00) 00000-0000"
        });

        // CEP
        $('input[name*="cep"], input[id*="cep"]').mask(UX_CONFIG.masks.cep, {
            placeholder: "00000-000"
        });

        // CPF
        $('input[name*="cpf"], input[id*="cpf"]').mask(UX_CONFIG.masks.cpf, {
            placeholder: "000.000.000-00"
        });

        // CNPJ
        $('input[name*="cnpj"], input[id*="cnpj"]').mask(UX_CONFIG.masks.cnpj, {
            placeholder: "00.000.000/0000-00"
        });

        // Data
        $('input[type="date"], input[name*="data"], input[id*="data"]').mask(UX_CONFIG.masks.date, {
            placeholder: "00/00/0000"
        });

        // Moeda
        $('input[name*="preco"], input[name*="valor"], input[id*="preco"], input[id*="valor"]').mask(UX_CONFIG.masks.currency, {
            reverse: true,
            placeholder: "0,00"
        });

        console.log('✅ Máscaras de input aplicadas com sucesso');
    }

    // Método para aplicar máscara específica
    applySpecificMask(selector, maskType) {
        if (UX_CONFIG.masks[maskType]) {
            $(selector).mask(UX_CONFIG.masks[maskType]);
        }
    }
}

/**
 * ===== SISTEMA DE VALIDAÇÃO EM TEMPO REAL =====
 */
class RealTimeValidator {
    constructor() {
        this.validators = {};
        this.initValidators();
    }

    initValidators() {
        // Validador de email
        this.validators.email = (value) => {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return {
                isValid: emailRegex.test(value),
                message: emailRegex.test(value) ? 'Email válido' : 'Email inválido'
            };
        };

        // Validador de CPF
        this.validators.cpf = (value) => {
            const cpf = value.replace(/[^\d]/g, '');
            if (cpf.length !== 11) return { isValid: false, message: 'CPF deve ter 11 dígitos' };
            
            // Lógica de validação de CPF
            let sum = 0;
            for (let i = 0; i < 9; i++) {
                sum += parseInt(cpf.charAt(i)) * (10 - i);
            }
            let remainder = 11 - (sum % 11);
            if (remainder === 10 || remainder === 11) remainder = 0;
            if (remainder !== parseInt(cpf.charAt(9))) {
                return { isValid: false, message: 'CPF inválido' };
            }

            sum = 0;
            for (let i = 0; i < 10; i++) {
                sum += parseInt(cpf.charAt(i)) * (11 - i);
            }
            remainder = 11 - (sum % 11);
            if (remainder === 10 || remainder === 11) remainder = 0;
            if (remainder !== parseInt(cpf.charAt(10))) {
                return { isValid: false, message: 'CPF inválido' };
            }

            return { isValid: true, message: 'CPF válido' };
        };

        // Validador de telefone
        this.validators.phone = (value) => {
            const phone = value.replace(/[^\d]/g, '');
            const isValid = phone.length === 10 || phone.length === 11;
            return {
                isValid,
                message: isValid ? 'Telefone válido' : 'Telefone deve ter 10 ou 11 dígitos'
            };
        };

        // Validador de CEP
        this.validators.cep = (value) => {
            const cep = value.replace(/[^\d]/g, '');
            const isValid = cep.length === 8;
            return {
                isValid,
                message: isValid ? 'CEP válido' : 'CEP deve ter 8 dígitos'
            };
        };

        this.attachValidators();
    }

    attachValidators() {
        // Email
        $('input[type="email"], input[name*="email"], input[id*="email"]').on('input', 
            this.debounce((e) => this.validateField(e.target, 'email'), UX_CONFIG.validation.debounceTime)
        );

        // CPF
        $('input[name*="cpf"], input[id*="cpf"]').on('input', 
            this.debounce((e) => this.validateField(e.target, 'cpf'), UX_CONFIG.validation.debounceTime)
        );

        // Telefone
        $('input[name*="telefone"], input[id*="telefone"], input[type="tel"]').on('input', 
            this.debounce((e) => this.validateField(e.target, 'phone'), UX_CONFIG.validation.debounceTime)
        );

        // CEP
        $('input[name*="cep"], input[id*="cep"]').on('input', 
            this.debounce((e) => this.validateField(e.target, 'cep'), UX_CONFIG.validation.debounceTime)
        );
    }

    validateField(field, validatorType) {
        const $field = $(field);
        const value = $field.val();
        
        if (!value) {
            this.clearValidation($field);
            return;
        }

        const result = this.validators[validatorType](value);
        this.applyValidationResult($field, result);
    }

    applyValidationResult($field, result) {
        const $fieldGroup = $field.closest('.field-group');
        
        if ($fieldGroup.length === 0) {
            // Criar wrapper se não existir
            $field.wrap('<div class="field-group"></div>');
            $field.parent().append('<i class="field-icon fas"></i>');
            $field.parent().append('<div class="field-message"></div>');
        }

        const $group = $field.closest('.field-group');
        const $icon = $group.find('.field-icon');
        const $message = $group.find('.field-message');

        // Remover classes anteriores
        $group.removeClass('valid invalid');
        $field.removeClass('is-valid is-invalid');

        if (result.isValid) {
            $group.addClass('valid');
            $field.addClass('is-valid');
            $icon.removeClass('fa-times-circle').addClass('fa-check-circle');
            $message.text(result.message);
        } else {
            $group.addClass('invalid');
            $field.addClass('is-invalid');
            $icon.removeClass('fa-check-circle').addClass('fa-times-circle');
            $message.text(result.message);
        }
    }

    clearValidation($field) {
        const $group = $field.closest('.field-group');
        $group.removeClass('valid invalid');
        $field.removeClass('is-valid is-invalid');
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

/**
 * ===== SISTEMA DE INDICADORES DE PROGRESSO =====
 */
class ProgressIndicator {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 3;
        this.initProgressBars();
    }

    initProgressBars() {
        this.createStepIndicator();
        this.updateProgress();
    }

    createStepIndicator() {
        // Verificar se já existe um indicador
        if ($('.step-indicator').length > 0) return;

        const $progressContainer = $('.progress-container');
        if ($progressContainer.length === 0) return;

        const stepIndicatorHTML = `
            <div class="step-indicator">
                <div class="step ${this.currentStep >= 1 ? 'completed' : ''}" data-step="1">
                    <span>1</span>
                </div>
                <div class="step ${this.currentStep >= 2 ? 'completed' : ''} ${this.currentStep === 2 ? 'active' : ''}" data-step="2">
                    <span>2</span>
                </div>
                <div class="step ${this.currentStep >= 3 ? 'completed' : ''} ${this.currentStep === 3 ? 'active' : ''}" data-step="3">
                    <span>3</span>
                </div>
            </div>
        `;

        $progressContainer.append(stepIndicatorHTML);
    }

    updateProgress(step = null) {
        if (step) this.currentStep = step;

        const progressPercentage = (this.currentStep / this.totalSteps) * 100;
        
        // Atualizar barra de progresso
        $('.progress-bar').css('width', `${progressPercentage}%`);
        
        // Atualizar indicador de etapas
        $('.step').each((index, element) => {
            const $step = $(element);
            const stepNumber = index + 1;
            
            $step.removeClass('active completed');
            
            if (stepNumber < this.currentStep) {
                $step.addClass('completed');
            } else if (stepNumber === this.currentStep) {
                $step.addClass('active');
            }
        });

        // Animação suave
        $('.progress-bar').addClass('progress-animated');
        setTimeout(() => {
            $('.progress-bar').removeClass('progress-animated');
        }, 600);
    }

    nextStep() {
        if (this.currentStep < this.totalSteps) {
            this.currentStep++;
            this.updateProgress();
        }
    }

    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateProgress();
        }
    }
}

/**
 * ===== SISTEMA DE FEEDBACK VISUAL =====
 */
class VisualFeedback {
    constructor() {
        this.initButtonEnhancements();
        this.initTooltips();
        this.initAnimations();
    }

    initButtonEnhancements() {
        // Adicionar classe enhanced aos botões
        $('.btn').addClass('btn-enhanced');

        // Loading states para formulários
        $('form').on('submit', function(e) {
            const $submitBtn = $(this).find('button[type="submit"]');
            $submitBtn.addClass('btn-loading');
            $submitBtn.prop('disabled', true);

            // Simular delay para demonstração
            setTimeout(() => {
                // Em produção, isso seria removido quando a resposta chegasse
                if (!$(this).find('.is-invalid').length) {
                    $submitBtn.removeClass('btn-loading');
                    $submitBtn.prop('disabled', false);
                }
            }, 2000);
        });
    }

    initTooltips() {
        // Inicializar tooltips personalizados
        $('[data-tooltip]').addClass('tooltip-enhanced');
        
        // Inicializar tooltips do Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    initAnimations() {
        // Adicionar animações aos elementos quando entram na viewport
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        });

        // Observar elementos com classe animate-on-scroll
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    }

    showNotification(message, type = 'info', duration = 3000) {
        const notificationHTML = `
            <div class="notification notification-${type} fade-in">
                <div class="notification-content">
                    <i class="fas fa-${this.getIconForType(type)}"></i>
                    <span>${message}</span>
                </div>
                <button class="notification-close" onclick="this.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        $('body').append(notificationHTML);

        // Auto-remove após duração especificada
        setTimeout(() => {
            $('.notification').last().fadeOut(() => {
                $(this).remove();
            });
        }, duration);
    }

    getIconForType(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

/**
 * ===== SISTEMA DE VALIDAÇÃO DE SENHA =====
 */
class PasswordStrengthMeter {
    constructor() {
        this.initPasswordFields();
    }

    initPasswordFields() {
        // Encontrar campos de senha
        const passwordFields = $('input[type="password"]');
        
        passwordFields.each((index, field) => {
            const $field = $(field);
            
            // Adicionar medidor de força se for campo de nova senha
            if ($field.attr('name') === 'password1' || $field.attr('name') === 'new_password1') {
                this.addStrengthMeter($field);
            }
        });
    }

    addStrengthMeter($field) {
        const meterHTML = `
            <div class="strength-meter">
                <div class="strength-bar">
                    <div class="strength-fill"></div>
                </div>
                <div class="strength-text"></div>
                <ul class="strength-requirements">
                    <li class="unmet" data-requirement="length">
                        <i class="fas fa-times-circle"></i> Mínimo 8 caracteres
                    </li>
                    <li class="unmet" data-requirement="uppercase">
                        <i class="fas fa-times-circle"></i> Letra maiúscula
                    </li>
                    <li class="unmet" data-requirement="lowercase">
                        <i class="fas fa-times-circle"></i> Letra minúscula
                    </li>
                    <li class="unmet" data-requirement="number">
                        <i class="fas fa-times-circle"></i> Número
                    </li>
                    <li class="unmet" data-requirement="special">
                        <i class="fas fa-times-circle"></i> Caractere especial
                    </li>
                </ul>
            </div>
        `;

        $field.after(meterHTML);
        
        // Adicionar evento de input
        $field.on('input', (e) => {
            this.updateStrengthMeter($(e.target));
        });
    }

    updateStrengthMeter($field) {
        const password = $field.val();
        const $meter = $field.siblings('.strength-meter');
        const $fill = $meter.find('.strength-fill');
        const $text = $meter.find('.strength-text');
        const $requirements = $meter.find('.strength-requirements li');

        // Critérios de validação
        const requirements = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        // Atualizar indicadores visuais dos requisitos
        Object.keys(requirements).forEach(key => {
            const $requirement = $requirements.filter(`[data-requirement="${key}"]`);
            const $icon = $requirement.find('i');
            
            if (requirements[key]) {
                $requirement.removeClass('unmet').addClass('met');
                $icon.removeClass('fa-times-circle').addClass('fa-check-circle');
            } else {
                $requirement.removeClass('met').addClass('unmet');
                $icon.removeClass('fa-check-circle').addClass('fa-times-circle');
            }
        });

        // Calcular força
        const metRequirements = Object.values(requirements).filter(Boolean).length;
        const strength = metRequirements / 5;

        // Atualizar barra de progresso
        $fill.css('width', `${strength * 100}%`);

        // Atualizar classes de cor
        $fill.removeClass('weak fair good strong');
        
        if (strength <= 0.25) {
            $fill.addClass('weak');
            $text.text('Muito fraca');
        } else if (strength <= 0.5) {
            $fill.addClass('fair');
            $text.text('Fraca');
        } else if (strength <= 0.75) {
            $fill.addClass('good');
            $text.text('Boa');
        } else {
            $fill.addClass('strong');
            $text.text('Forte');
        }
    }
}

/**
 * ===== SISTEMA DE OTIMIZAÇÃO MOBILE =====
 */
class MobileOptimizer {
    constructor() {
        this.initMobileOptimizations();
    }

    initMobileOptimizations() {
        // Detectar dispositivos móveis
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        if (isMobile) {
            this.applyMobileOptimizations();
        }

        // Otimizações baseadas no tamanho da tela
        this.handleResponsiveChanges();
    }

    applyMobileOptimizations() {
        // Adicionar classe mobile ao body
        $('body').addClass('mobile-device');

        // Otimizar inputs para mobile
        $('input[type="text"], input[type="email"], input[type="tel"]').attr('autocomplete', 'on');
        
        // Melhorar área de toque
        $('.btn, .form-control, .form-check-input').addClass('touch-optimized');

        // Scroll suave
        $('html').css('scroll-behavior', 'smooth');
    }

    handleResponsiveChanges() {
        $(window).on('resize', () => {
            if ($(window).width() < 768) {
                // Modo mobile
                $('.card').addClass('mobile-card');
                $('.progress-enhanced').addClass('mobile-progress');
            } else {
                // Modo desktop
                $('.card').removeClass('mobile-card');
                $('.progress-enhanced').removeClass('mobile-progress');
            }
        });

        // Trigger inicial
        $(window).trigger('resize');
    }
}

/**
 * ===== INICIALIZAÇÃO =====
 */
$(document).ready(function() {
    console.log('🚀 Iniciando sistema de melhorias UX...');

    // Inicializar todos os sistemas
    const maskManager = new InputMaskManager();
    const validator = new RealTimeValidator();
    const progressIndicator = new ProgressIndicator();
    const visualFeedback = new VisualFeedback();
    const passwordMeter = new PasswordStrengthMeter();
    const mobileOptimizer = new MobileOptimizer();

    // Expor para uso global
    window.UXEnhancements = {
        maskManager,
        validator,
        progressIndicator,
        visualFeedback,
        passwordMeter,
        mobileOptimizer
    };

    console.log('✅ Sistema de melhorias UX inicializado com sucesso!');
});

/**
 * ===== UTILITÁRIOS GLOBAIS =====
 */

// Função para toggle de senha
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const icon = field.nextElementSibling.querySelector('i');
    
    if (field.type === 'password') {
        field.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        field.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

// Função para buscar CEP
function buscarCEP(cep) {
    const cepLimpo = cep.replace(/\D/g, '');
    
    if (cepLimpo.length === 8) {
        $.get(`https://viacep.com.br/ws/${cepLimpo}/json/`, function(data) {
            if (!data.erro) {
                $('#id_endereco').val(data.logradouro);
                $('#id_bairro').val(data.bairro);
                $('#id_cidade').val(data.localidade);
                $('#id_estado').val(data.uf);
                
                // Feedback visual
                window.UXEnhancements.visualFeedback.showNotification(
                    'CEP encontrado! Endereço preenchido automaticamente.',
                    'success'
                );
            }
        });
    }
}

// Auto-buscar CEP quando campo for preenchido
$(document).on('blur', 'input[name*="cep"], input[id*="cep"]', function() {
    const cep = $(this).val();
    if (cep.length >= 8) {
        buscarCEP(cep);
    }
});

// Smooth scroll para âncoras
$(document).on('click', 'a[href^="#"]', function(e) {
    e.preventDefault();
    const target = $(this.getAttribute('href'));
    if (target.length) {
        $('html, body').animate({
            scrollTop: target.offset().top - 100
        }, 500);
    }
});

console.log('📱 UX Enhancements carregado com sucesso!'); 