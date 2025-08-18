/**
 * LGPD Cookie Consent Management System
 * Compliant with Lei Geral de Proteção de Dados (LGPD)
 */

class LGPDConsentManager {
    constructor() {
        this.cookieName = 'lgpd_consent';
        this.consentDuration = 365; // days
        this.banner = null;
        this.settingsBtn = null;
        this.modal = null;
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        this.banner = document.getElementById('lgpd-cookie-banner');
        this.settingsBtn = document.getElementById('cookie-settings-btn');
        this.modal = document.getElementById('lgpd-preferences-modal');

        if (!this.banner) {
            console.warn('LGPD banner not found');
            return;
        }

        this.bindEvents();
        this.checkConsentStatus();
        this.loadConsentPreferences();
        console.log('LGPD Consent Manager initialized');
    }

    bindEvents() {
        // Banner buttons
        const acceptAllBtn = document.getElementById('lgpd-accept-all');
        const rejectOptionalBtn = document.getElementById('lgpd-reject-optional');
        const manageBtn = document.getElementById('lgpd-manage-cookies');
        const savePreferencesBtn = document.getElementById('save-cookie-preferences');

        if (acceptAllBtn) {
            acceptAllBtn.addEventListener('click', () => this.acceptAllCookies());
        }

        if (rejectOptionalBtn) {
            rejectOptionalBtn.addEventListener('click', () => this.acceptEssentialOnly());
        }

        if (manageBtn) {
            manageBtn.addEventListener('click', () => this.showPreferencesModal());
        }

        if (savePreferencesBtn) {
            savePreferencesBtn.addEventListener('click', () => this.savePreferences());
        }

        // Log consent interactions for compliance
        document.addEventListener('click', (e) => {
            if (e.target.closest('.lgpd-banner') || e.target.closest('#lgpd-preferences-modal')) {
                this.logConsentInteraction(e.target.textContent || e.target.value || 'interaction');
            }
        });
    }

    checkConsentStatus() {
        const consent = this.getConsent();
        
        if (!consent || this.isConsentExpired(consent)) {
            this.showBanner();
        } else {
            this.hideBanner();
            this.showSettingsButton();
            this.applyCookiePreferences(consent);
        }
    }

    showBanner() {
        if (this.banner) {
            this.banner.style.display = 'block';
            // Adjust body padding to account for banner
            document.body.style.paddingBottom = this.banner.offsetHeight + 'px';
            
            // Log banner display
            this.logConsentInteraction('banner_displayed');
        }
    }

    hideBanner() {
        if (this.banner) {
            this.banner.style.display = 'none';
            document.body.style.paddingBottom = '';
        }
    }

    showSettingsButton() {
        if (this.settingsBtn) {
            this.settingsBtn.style.display = 'block';
        }
    }

    acceptAllCookies() {
        const consent = {
            essential: true,
            analytics: true,
            marketing: true,
            preferences: true,
            timestamp: Date.now(),
            version: '1.0'
        };

        this.saveConsent(consent);
        this.applyCookiePreferences(consent);
        this.hideBanner();
        this.showSettingsButton();
        this.showConsentMessage('Todas as preferências de cookies foram aceitas.', 'success');
        
        this.logConsentInteraction('accept_all_cookies');
    }

    acceptEssentialOnly() {
        const consent = {
            essential: true,
            analytics: false,
            marketing: false,
            preferences: false,
            timestamp: Date.now(),
            version: '1.0'
        };

        this.saveConsent(consent);
        this.applyCookiePreferences(consent);
        this.hideBanner();
        this.showSettingsButton();
        this.showConsentMessage('Apenas cookies essenciais foram aceitos.', 'info');
        
        this.logConsentInteraction('accept_essential_only');
    }

    showPreferencesModal() {
        if (this.modal) {
            // Bootstrap modal show
            const bsModal = new bootstrap.Modal(this.modal);
            bsModal.show();
            
            this.logConsentInteraction('preferences_modal_opened');
        }
    }

    savePreferences() {
        const essential = document.getElementById('essential-cookies')?.checked || false;
        const analytics = document.getElementById('analytics-cookies')?.checked || false;
        const marketing = document.getElementById('marketing-cookies')?.checked || false;
        const preferences = document.getElementById('preferences-cookies')?.checked || false;

        const consent = {
            essential: true, // Always true
            analytics: analytics,
            marketing: marketing,
            preferences: preferences,
            timestamp: Date.now(),
            version: '1.0'
        };

        this.saveConsent(consent);
        this.applyCookiePreferences(consent);
        this.hideBanner();
        this.showSettingsButton();

        // Close modal
        const bsModal = bootstrap.Modal.getInstance(this.modal);
        if (bsModal) {
            bsModal.hide();
        }

        this.showConsentMessage('Suas preferências de cookies foram salvas.', 'success');
        
        this.logConsentInteraction('custom_preferences_saved');
    }

    loadConsentPreferences() {
        const consent = this.getConsent();
        if (consent) {
            // Update modal checkboxes
            const analyticsCheckbox = document.getElementById('analytics-cookies');
            const marketingCheckbox = document.getElementById('marketing-cookies');
            const preferencesCheckbox = document.getElementById('preferences-cookies');

            if (analyticsCheckbox) analyticsCheckbox.checked = consent.analytics || false;
            if (marketingCheckbox) marketingCheckbox.checked = consent.marketing || false;
            if (preferencesCheckbox) preferencesCheckbox.checked = consent.preferences || false;
        }
    }

    applyCookiePreferences(consent) {
        // Apply analytics cookies
        if (consent.analytics) {
            this.enableAnalytics();
        } else {
            this.disableAnalytics();
        }

        // Apply marketing cookies
        if (consent.marketing) {
            this.enableMarketing();
        } else {
            this.disableMarketing();
        }

        // Apply preferences cookies
        if (consent.preferences) {
            this.enablePreferences();
        } else {
            this.disablePreferences();
        }

        // Log preference application
        this.logConsentInteraction('preferences_applied', consent);
    }

    enableAnalytics() {
        // Enable Google Analytics or other analytics tools
        console.log('Analytics cookies enabled');
        
        // Example: Load Google Analytics
        // gtag('config', 'GA_MEASUREMENT_ID');
        
        // Set analytics cookies consent
        this.setCookie('analytics_enabled', 'true', this.consentDuration);
    }

    disableAnalytics() {
        console.log('Analytics cookies disabled');
        
        // Remove analytics cookies
        this.deleteCookie('_ga');
        this.deleteCookie('_ga_*');
        this.deleteCookie('_gid');
        this.deleteCookie('_gat');
        this.deleteCookie('analytics_enabled');
        
        // Disable Google Analytics tracking
        if (typeof gtag === 'function') {
            gtag('consent', 'update', {
                'analytics_storage': 'denied'
            });
        }
    }

    enableMarketing() {
        console.log('Marketing cookies enabled');
        this.setCookie('marketing_enabled', 'true', this.consentDuration);
        
        // Enable marketing tools (Facebook Pixel, etc.)
        if (typeof gtag === 'function') {
            gtag('consent', 'update', {
                'ad_storage': 'granted'
            });
        }
    }

    disableMarketing() {
        console.log('Marketing cookies disabled');
        
        // Remove marketing cookies
        this.deleteCookie('_fbp');
        this.deleteCookie('_fbc');
        this.deleteCookie('marketing_enabled');
        
        // Disable marketing tools
        if (typeof gtag === 'function') {
            gtag('consent', 'update', {
                'ad_storage': 'denied'
            });
        }
    }

    enablePreferences() {
        console.log('Preferences cookies enabled');
        this.setCookie('preferences_enabled', 'true', this.consentDuration);
    }

    disablePreferences() {
        console.log('Preferences cookies disabled');
        this.deleteCookie('preferences_enabled');
        
        // Remove user preference cookies but keep essential ones
        const cookies = document.cookie.split(';');
        cookies.forEach(cookie => {
            const name = cookie.split('=')[0].trim();
            if (name.startsWith('pref_') || name.startsWith('user_setting_')) {
                this.deleteCookie(name);
            }
        });
    }

    saveConsent(consent) {
        const consentString = JSON.stringify(consent);
        this.setCookie(this.cookieName, consentString, this.consentDuration);
        console.log('Consent saved:', consent);
    }

    getConsent() {
        const consentCookie = this.getCookie(this.cookieName);
        if (consentCookie) {
            try {
                return JSON.parse(consentCookie);
            } catch (e) {
                console.error('Error parsing consent cookie:', e);
                return null;
            }
        }
        return null;
    }

    isConsentExpired(consent) {
        if (!consent || !consent.timestamp) {
            return true;
        }
        
        const expirationTime = consent.timestamp + (this.consentDuration * 24 * 60 * 60 * 1000);
        return Date.now() > expirationTime;
    }

    setCookie(name, value, days) {
        const expires = new Date(Date.now() + days * 24 * 60 * 60 * 1000);
        document.cookie = `${name}=${value}; expires=${expires.toUTCString()}; path=/; SameSite=Lax`;
    }

    getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    }

    deleteCookie(name) {
        // Delete cookie with different path options
        const paths = ['/', '/admin/', '/api/'];
        const domains = [window.location.hostname, '.' + window.location.hostname];
        
        paths.forEach(path => {
            domains.forEach(domain => {
                document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=${path}; domain=${domain}`;
                document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=${path}`;
            });
        });
    }

    showConsentMessage(message, type = 'info') {
        // Create and show a temporary message
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 10000; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    }

    logConsentInteraction(action, data = null) {
        // Log consent interactions for compliance audit trail
        const logEntry = {
            timestamp: new Date().toISOString(),
            action: action,
            userAgent: navigator.userAgent,
            url: window.location.href,
            data: data
        };
        
        console.log('LGPD Consent Log:', logEntry);
        
        // Send to backend for audit logging (optional)
        if (typeof fetch !== 'undefined') {
            fetch('/api/v1/lgpd/consent-log/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(logEntry)
            }).catch(error => {
                console.warn('Failed to log consent interaction:', error);
            });
        }
    }

    getCSRFToken() {
        const cookieValue = this.getCookie('csrftoken');
        return cookieValue || '';
    }

    // Public API methods
    updateConsent() {
        this.showPreferencesModal();
    }

    revokeConsent() {
        this.deleteCookie(this.cookieName);
        this.disableAnalytics();
        this.disableMarketing();
        this.disablePreferences();
        this.showBanner();
        this.logConsentInteraction('consent_revoked');
        this.showConsentMessage('Seu consentimento foi revogado. Configure suas preferências novamente.', 'warning');
    }

    getConsentStatus() {
        return this.getConsent();
    }
}

// Initialize LGPD Consent Manager
const lgpdConsent = new LGPDConsentManager();

// Expose to global scope for external access
window.LGPDConsent = lgpdConsent;

// Google Analytics consent mode (if GA is used)
window.dataLayer = window.dataLayer || [];
function gtag() { dataLayer.push(arguments); }

// Set default consent state
if (typeof gtag === 'function') {
    gtag('consent', 'default', {
        'ad_storage': 'denied',
        'analytics_storage': 'denied',
        'functionality_storage': 'granted',
        'personalization_storage': 'denied',
        'security_storage': 'granted'
    });
}