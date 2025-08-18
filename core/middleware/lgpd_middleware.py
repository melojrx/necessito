"""
LGPD Compliance Middleware
Handles cookie consent, data processing logs, and compliance features.
"""

import json
import logging
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)


class LGPDConsentMiddleware(MiddlewareMixin):
    """
    Middleware to handle LGPD cookie consent and data processing compliance.
    """
    
    CONSENT_COOKIE_NAME = 'lgpd_consent'
    CONSENT_LOG_COOKIE_NAME = 'lgpd_consent_log'
    CONSENT_EXPIRY_DAYS = 365
    
    # URLs that don't require consent checking
    EXEMPT_URLS = [
        '/admin/',
        '/api/v1/lgpd/',
        '/politica-de-privacidade/',
        '/termos-de-uso/',
        '/static/',
        '/media/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Process incoming requests for LGPD compliance.
        """
        # Skip processing for exempt URLs
        if any(request.path.startswith(url) for url in self.EXEMPT_URLS):
            return None
        
        # Add consent information to request
        request.lgpd_consent = self.get_user_consent(request)
        request.lgpd_consent_required = self.is_consent_required(request)
        
        # Log data processing activity
        self.log_data_processing(request)
        
        return None
    
    def process_response(self, request, response):
        """
        Process responses to handle cookie consent.
        """
        # Skip processing for exempt URLs
        if any(request.path.startswith(url) for url in self.EXEMPT_URLS):
            return response
        
        # Handle non-essential cookie blocking if consent not given
        if hasattr(request, 'lgpd_consent'):
            consent = request.lgpd_consent
            if consent and not consent.get('analytics', False):
                # Block analytics cookies
                self.block_analytics_cookies(response)
            
            if consent and not consent.get('marketing', False):
                # Block marketing cookies
                self.block_marketing_cookies(response)
        
        return response
    
    def get_user_consent(self, request):
        """
        Retrieve and validate user's LGPD consent from cookies.
        """
        consent_cookie = request.COOKIES.get(self.CONSENT_COOKIE_NAME)
        if not consent_cookie:
            return None
        
        try:
            consent_data = json.loads(consent_cookie)
            
            # Validate consent structure
            required_fields = ['essential', 'analytics', 'marketing', 'preferences', 'timestamp', 'version']
            if not all(field in consent_data for field in required_fields):
                logger.warning(f"Invalid consent structure for user {request.user.id if hasattr(request, 'user') else 'anonymous'}")
                return None
            
            # Check if consent has expired
            consent_timestamp = consent_data.get('timestamp', 0)
            expiry_timestamp = consent_timestamp + (self.CONSENT_EXPIRY_DAYS * 24 * 60 * 60 * 1000)
            
            if datetime.now().timestamp() * 1000 > expiry_timestamp:
                logger.info(f"Consent expired for user {request.user.id if hasattr(request, 'user') else 'anonymous'}")
                return None
            
            return consent_data
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing consent cookie: {e}")
            return None
    
    def is_consent_required(self, request):
        """
        Determine if consent is required for this request.
        """
        # Consent is always required for non-essential cookie operations
        # Essential cookies (session, CSRF, authentication) don't require consent
        
        # Check if request involves non-essential operations
        non_essential_patterns = [
            'analytics',
            'marketing',
            'tracking',
            'advertisement'
        ]
        
        path_lower = request.path.lower()
        return any(pattern in path_lower for pattern in non_essential_patterns)
    
    def block_analytics_cookies(self, response):
        """
        Block analytics cookies if consent not given.
        """
        analytics_cookies = [
            '_ga', '_ga_*', '_gid', '_gat', 'analytics_enabled'
        ]
        
        for cookie_name in analytics_cookies:
            if cookie_name in response.cookies:
                response.delete_cookie(cookie_name)
    
    def block_marketing_cookies(self, response):
        """
        Block marketing cookies if consent not given.
        """
        marketing_cookies = [
            '_fbp', '_fbc', 'marketing_enabled'
        ]
        
        for cookie_name in marketing_cookies:
            if cookie_name in response.cookies:
                response.delete_cookie(cookie_name)
    
    def log_data_processing(self, request):
        """
        Log data processing activities for LGPD compliance audit.
        """
        try:
            # Only log if user has given consent or for essential processing
            consent = getattr(request, 'lgpd_consent', None)
            user_id = None
            
            if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
                user_id = request.user.id
            
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'path': request.path,
                'method': request.method,
                'consent_status': consent is not None,
                'consent_details': consent if consent else {},
                'session_key': request.session.session_key if hasattr(request, 'session') else None
            }
            
            # Log to Django logger (should be configured to write to audit file)
            logger.info(f"LGPD_DATA_PROCESSING: {json.dumps(log_entry)}")
            
        except Exception as e:
            logger.error(f"Error logging data processing activity: {e}")
    
    def get_client_ip(self, request):
        """
        Get client IP address from request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        else:
            return request.META.get('REMOTE_ADDR', '')


class LGPDDataMinimizationMiddleware(MiddlewareMixin):
    """
    Middleware to enforce data minimization principles.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Check and limit data collection based on LGPD principles.
        """
        # Remove unnecessary headers that might contain personal data
        sensitive_headers = [
            'HTTP_X_REAL_IP',
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_FORWARDED_HOST'
        ]
        
        # Only keep these headers if user has given consent
        consent = getattr(request, 'lgpd_consent', None)
        if not consent or not consent.get('analytics', False):
            for header in sensitive_headers:
                if header in request.META:
                    # Keep for essential functionality but mark as sensitive
                    request.META[f'{header}_SENSITIVE'] = request.META[header]
        
        return None


class LGPDResponseHeadersMiddleware(MiddlewareMixin):
    """
    Add LGPD-compliant security and privacy headers.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_response(self, request, response):
        """
        Add privacy and security headers to responses.
        """
        # Add privacy-related headers
        response['Permissions-Policy'] = (
            'camera=(), '
            'microphone=(), '
            'geolocation=(self), '
            'interest-cohort=()'
        )
        
        # Referrer policy for privacy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        if not response.get('Content-Security-Policy'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com https://cdnjs.cloudflare.com https://unpkg.com https://www.google.com https://www.gstatic.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com https://unpkg.com; "
                "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://api.github.com https://www.google.com https://www.gstatic.com; "
                "frame-src 'self' https://www.google.com https://recaptcha.google.com; "
                "child-src 'self' https://www.google.com https://recaptcha.google.com"
            )
        
        # Cookie SameSite policy
        if hasattr(response, 'cookies'):
            for cookie in response.cookies.values():
                if not cookie.get('samesite'):
                    cookie['samesite'] = 'Lax'
                if not cookie.get('secure') and request.is_secure():
                    cookie['secure'] = True
        
        return response


# API endpoint for consent logging
def lgpd_consent_log_view(request):
    """
    API endpoint to log consent interactions.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['timestamp', 'action']
        if not all(field in data for field in required_fields):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Log consent interaction
        user_id = None
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            user_id = request.user.id
        
        log_entry = {
            'type': 'consent_interaction',
            'user_id': user_id,
            'ip_address': LGPDConsentMiddleware().get_client_ip(request),
            'session_key': request.session.session_key if hasattr(request, 'session') else None,
            'interaction_data': data
        }
        
        logger.info(f"LGPD_CONSENT_INTERACTION: {json.dumps(log_entry)}")
        
        return JsonResponse({'status': 'logged'})
        
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Error logging consent interaction: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)