"""
Configuração de versionamento da API do Indicai.

Este módulo centraliza as configurações de versionamento da API,
facilitando a manutenção e evolução das versões.
"""

# Versão atual da API
CURRENT_API_VERSION = 'v1'

# Versões suportadas
SUPPORTED_VERSIONS = ['v1']

# Versões descontinuadas (para futuro uso)
DEPRECATED_VERSIONS = []

# Metadados das versões
VERSION_METADATA = {
    'v1': {
        'version': '1.0.0',
        'status': 'stable',
        'description': 'Primeira versão estável da API do Indicai',
        'release_date': '2025-01-20',
        'features': [
            'Autenticação JWT',
            'CRUD de usuários',
            'Gestão de categorias e subcategorias',
            'Gestão de necessidades (anúncios)',
            'Sistema de orçamentos',
            'Sistema de avaliações',
        ],
        'breaking_changes': [],
        'deprecation_notice': None,
    }
}

def get_version_info(version):
    """
    Retorna informações sobre uma versão específica da API.
    
    Args:
        version (str): Versão da API (ex: 'v1')
        
    Returns:
        dict: Metadados da versão ou None se não encontrada
    """
    return VERSION_METADATA.get(version)

def is_version_supported(version):
    """
    Verifica se uma versão da API é suportada.
    
    Args:
        version (str): Versão da API
        
    Returns:
        bool: True se a versão é suportada
    """
    return version in SUPPORTED_VERSIONS

def is_version_deprecated(version):
    """
    Verifica se uma versão da API está descontinuada.
    
    Args:
        version (str): Versão da API
        
    Returns:
        bool: True se a versão está descontinuada
    """
    return version in DEPRECATED_VERSIONS 