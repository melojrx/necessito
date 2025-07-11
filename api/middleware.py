"""
Middleware para versionamento da API do Indicai.
"""
from django.utils.deprecation import MiddlewareMixin
from .versions import CURRENT_API_VERSION, VERSION_METADATA, is_version_deprecated
import re


class APIVersionMiddleware(MiddlewareMixin):
    """
    Middleware que adiciona headers de versionamento nas respostas da API
    e processa informações sobre versões descontinuadas.
    """
    
    def process_response(self, request, response):
        """
        Adiciona headers de versionamento nas respostas da API.
        """
        # Verifica se é uma requisição para a API
        if request.path.startswith('/api/'):
            # Extrai a versão da URL
            version_match = re.match(r'/api/v(\d+)/', request.path)
            if version_match:
                version = f"v{version_match.group(1)}"
            else:
                # Se não há versão na URL, assume a versão atual
                version = CURRENT_API_VERSION
            
            # Adiciona headers de versionamento
            response['API-Version'] = version
            response['API-Current-Version'] = CURRENT_API_VERSION
            
            # Adiciona informações sobre a versão
            version_info = VERSION_METADATA.get(version)
            if version_info:
                response['API-Version-Status'] = version_info['status']
                
                # Adiciona aviso de descontinuação se necessário
                if is_version_deprecated(version):
                    response['API-Deprecation-Warning'] = (
                        f"API version {version} is deprecated. "
                        f"Please upgrade to {CURRENT_API_VERSION}."
                    )
                    
                # Adiciona informações sobre breaking changes
                if version_info.get('breaking_changes'):
                    response['API-Breaking-Changes'] = 'true'
        
        return response
    
    def process_request(self, request):
        """
        Processa a requisição para extrair informações de versionamento.
        """
        # Adiciona informações de versão ao objeto request para uso nas views
        if request.path.startswith('/api/'):
            version_match = re.match(r'/api/v(\d+)/', request.path)
            if version_match:
                request.api_version = f"v{version_match.group(1)}"
            else:
                request.api_version = CURRENT_API_VERSION
        
        return None 