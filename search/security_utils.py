"""
Utilitários de segurança para o sistema de busca.
Implementa validações de entrada, sanitização XSS e rate limiting.
"""

import re
import logging
import html
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone

# Configurar logger de segurança
security_logger = logging.getLogger('search.security')

# Constantes de validação
MAX_SEARCH_TERM_LENGTH = 100
MAX_LOCATION_LENGTH = 50
MAX_CLIENT_NAME_LENGTH = 50

# Padrões regex para validação
SAFE_SEARCH_PATTERN = re.compile(r'^[a-zA-Z0-9À-ÿ\s\-_,.()&]+$', re.UNICODE)
SAFE_LOCATION_PATTERN = re.compile(r'^[a-zA-Z0-9À-ÿ\s\-_,.()]+$', re.UNICODE)
SAFE_CLIENT_PATTERN = re.compile(r'^[a-zA-ZÀ-ÿ\s\-_]+$', re.UNICODE)

# Rate limiting
RATE_LIMIT_REQUESTS = 30  # máximo de requests por período
RATE_LIMIT_PERIOD = 60   # período em segundos


def sanitize_html(text):
    """
    Sanitiza texto removendo potenciais scripts XSS.
    Escapa HTML e remove caracteres perigosos.
    """
    if not text:
        return ""
    
    # Escapar HTML
    sanitized = html.escape(str(text).strip())
    
    # Remover caracteres de controle potencialmente perigosos
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
    
    return sanitized


def validate_search_term(term):
    """
    Valida termo de busca para prevenir XSS e ataques de injeção.
    
    Args:
        term (str): Termo a ser validado
        
    Returns:
        tuple: (is_valid, sanitized_term, error_message)
    """
    if not term:
        return True, "", None
    
    # Verificar comprimento
    if len(term) > MAX_SEARCH_TERM_LENGTH:
        security_logger.warning(f"Search term too long: {len(term)} characters")
        return False, "", f"Termo de busca muito longo (máximo {MAX_SEARCH_TERM_LENGTH} caracteres)"
    
    # Sanitizar HTML
    sanitized = sanitize_html(term)
    
    # Validar caracteres permitidos
    if not SAFE_SEARCH_PATTERN.match(sanitized):
        security_logger.warning(f"Invalid search term pattern: {term}")
        return False, "", "Termo contém caracteres não permitidos"
    
    # Detectar tentativas de script injection
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe',
        r'<object',
        r'<embed',
        r'eval\s*\(',
        r'expression\s*\(',
    ]
    
    term_lower = sanitized.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, term_lower, re.IGNORECASE):
            security_logger.error(f"Potential XSS attempt detected: {term}")
            return False, "", "Termo contém conteúdo suspeito"
    
    return True, sanitized, None


def validate_location(location):
    """
    Valida campo de localização.
    
    Args:
        location (str): Localização a ser validada
        
    Returns:
        tuple: (is_valid, sanitized_location, error_message)
    """
    if not location:
        return True, "", None
    
    if len(location) > MAX_LOCATION_LENGTH:
        security_logger.warning(f"Location too long: {len(location)} characters")
        return False, "", f"Localização muito longa (máximo {MAX_LOCATION_LENGTH} caracteres)"
    
    sanitized = sanitize_html(location)
    
    if not SAFE_LOCATION_PATTERN.match(sanitized):
        security_logger.warning(f"Invalid location pattern: {location}")
        return False, "", "Localização contém caracteres não permitidos"
    
    return True, sanitized, None


def validate_client_name(client_name):
    """
    Valida nome do cliente.
    
    Args:
        client_name (str): Nome do cliente a ser validado
        
    Returns:
        tuple: (is_valid, sanitized_name, error_message)
    """
    if not client_name:
        return True, "", None
    
    if len(client_name) > MAX_CLIENT_NAME_LENGTH:
        security_logger.warning(f"Client name too long: {len(client_name)} characters")
        return False, "", f"Nome muito longo (máximo {MAX_CLIENT_NAME_LENGTH} caracteres)"
    
    sanitized = sanitize_html(client_name)
    
    if not SAFE_CLIENT_PATTERN.match(sanitized):
        security_logger.warning(f"Invalid client name pattern: {client_name}")
        return False, "", "Nome contém caracteres não permitidos"
    
    return True, sanitized, None


def validate_coordinates(lat, lon):
    """
    Valida coordenadas de latitude e longitude.
    
    Args:
        lat (str): Latitude
        lon (str): Longitude
        
    Returns:
        tuple: (is_valid, lat_float, lon_float, error_message)
    """
    if not lat and not lon:
        return True, None, None, None
    
    try:
        if lat:
            lat_float = float(lat)
            if not (-90 <= lat_float <= 90):
                return False, None, None, "Latitude deve estar entre -90 e 90"
        else:
            lat_float = None
            
        if lon:
            lon_float = float(lon)
            if not (-180 <= lon_float <= 180):
                return False, None, None, "Longitude deve estar entre -180 e 180"
        else:
            lon_float = None
            
        return True, lat_float, lon_float, None
        
    except (ValueError, TypeError):
        security_logger.warning(f"Invalid coordinates: lat={lat}, lon={lon}")
        return False, None, None, "Coordenadas devem ser números válidos"


def get_client_ip(request):
    """
    Obtém o IP real do cliente considerando proxies.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def rate_limit_check(request, endpoint_name='autocomplete'):
    """
    Verifica se o cliente excedeu o rate limit.
    
    Args:
        request: Django request object
        endpoint_name (str): Nome do endpoint para cache
        
    Returns:
        tuple: (is_allowed, remaining_requests)
    """
    ip = get_client_ip(request)
    cache_key = f"rate_limit:{endpoint_name}:{ip}"
    
    # Verificar número atual de requests
    current_requests = cache.get(cache_key, 0)
    
    if current_requests >= RATE_LIMIT_REQUESTS:
        security_logger.warning(f"Rate limit exceeded for IP {ip} on {endpoint_name}")
        return False, 0
    
    # Incrementar contador
    cache.set(cache_key, current_requests + 1, RATE_LIMIT_PERIOD)
    
    remaining = RATE_LIMIT_REQUESTS - (current_requests + 1)
    return True, remaining


def rate_limit_decorator(endpoint_name='default'):
    """
    Decorator para aplicar rate limiting automaticamente.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            allowed, remaining = rate_limit_check(request, endpoint_name)
            
            if not allowed:
                return JsonResponse({
                    'error': 'Rate limit exceeded. Please try again later.',
                    'retry_after': RATE_LIMIT_PERIOD
                }, status=429)
            
            # Adicionar headers informativos
            response = view_func(request, *args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Remaining'] = str(remaining)
                response.headers['X-RateLimit-Limit'] = str(RATE_LIMIT_REQUESTS)
                response.headers['X-RateLimit-Reset'] = str(int(timezone.now().timestamp()) + RATE_LIMIT_PERIOD)
            
            return response
        return wrapper
    return decorator


def log_suspicious_activity(request, activity_type, details):
    """
    Registra atividade suspeita para monitoramento.
    
    Args:
        request: Django request object
        activity_type (str): Tipo de atividade suspeita
        details (str): Detalhes da atividade
    """
    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    
    security_logger.error(f"Suspicious activity: {activity_type} | IP: {ip} | User-Agent: {user_agent} | Details: {details}")


def validate_status_list(status_list):
    """
    Valida lista de status contra opções válidas do modelo.
    
    Args:
        status_list (list): Lista de status a validar
        
    Returns:
        list: Lista de status válidos
    """
    if not status_list:
        return ['ativo']
    
    # Status válidos definidos no modelo
    valid_statuses = ['ativo', 'inativo', 'finalizado', 'pausado']
    
    # Filtrar apenas status válidos
    validated = [s for s in status_list if s in valid_statuses]
    
    # Se nenhum status válido, usar padrão
    if not validated:
        validated = ['ativo']
        
    return validated


def validate_search_fields(fields_list):
    """
    Valida lista de campos de busca.
    
    Args:
        fields_list (list): Lista de campos a validar
        
    Returns:
        list: Lista de campos válidos
    """
    valid_fields = ['titulo', 'descricao', 'categoria', 'subcategoria']
    
    if not fields_list:
        return []
    
    # Filtrar apenas campos válidos
    validated = [f for f in fields_list if f in valid_fields]
    
    return validated