"""
Serviço de endereçamento integrado com APIs gratuitas
- ViaCEP: Busca de endereço por CEP
- Nominatim: Geocoding e autocomplete
"""

import requests
import json
import re
from typing import Dict, List, Optional, Tuple
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class AddressService:
    """Serviço centralizado para consultas de endereço"""
    
    # URLs das APIs
    VIACEP_URL = "https://viacep.com.br/ws/{}/json/"
    NOMINATIM_URL = "https://nominatim.openstreetmap.org"
    
    # Headers para requisições
    HEADERS = {
        'User-Agent': 'Indicai-Marketplace/1.0 (contato@indicai.com)'
    }
    
    @classmethod
    def clean_cep(cls, cep: str) -> str:
        """Remove formatação do CEP"""
        if not cep:
            return ""
        return re.sub(r'\D', '', cep)
    
    @classmethod
    def format_cep(cls, cep: str) -> str:
        """Formata CEP com hífen"""
        clean = cls.clean_cep(cep)
        if len(clean) == 8:
            return f"{clean[:5]}-{clean[5:]}"
        return clean
    
    @classmethod
    def get_address_by_cep(cls, cep: str) -> Dict:
        """
        Busca endereço completo pelo CEP usando ViaCEP
        
        Returns:
            Dict com dados do endereço ou erro
        """
        clean_cep = cls.clean_cep(cep)
        
        if len(clean_cep) != 8:
            return {
                'success': False,
                'error': 'CEP deve ter 8 dígitos'
            }
        
        # Cache key
        cache_key = f"address_cep_{clean_cep}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            url = cls.VIACEP_URL.format(clean_cep)
            response = requests.get(url, headers=cls.HEADERS, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('erro'):
                    result = {
                        'success': False,
                        'error': 'CEP não encontrado'
                    }
                else:
                    result = {
                        'success': True,
                        'data': {
                            'cep': cls.format_cep(data.get('cep', '')),
                            'logradouro': data.get('logradouro', ''),
                            'bairro': data.get('bairro', ''),
                            'cidade': data.get('localidade', ''),
                            'estado': data.get('uf', ''),
                            'complemento': data.get('complemento', ''),
                            'ibge': data.get('ibge', ''),
                            'gia': data.get('gia', ''),
                            'ddd': data.get('ddd', ''),
                            'siafi': data.get('siafi', ''),
                            'raw_data': data  # Dados originais da API
                        }
                    }
                
                # Cache por 24 horas
                cache.set(cache_key, result, 86400)
                return result
            
            else:
                return {
                    'success': False,
                    'error': f'Erro na API ViaCEP: {response.status_code}'
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar ViaCEP para CEP {clean_cep}: {e}")
            return {
                'success': False,
                'error': 'Erro de conexão com o serviço de CEP'
            }
        except Exception as e:
            logger.error(f"Erro inesperado ao consultar CEP {clean_cep}: {e}")
            return {
                'success': False,
                'error': 'Erro interno do servidor'
            }
    
    @classmethod
    def get_coordinates_by_address(cls, address: str, city: str = "", state: str = "") -> Dict:
        """
        Obtém coordenadas (lat, lon) de um endereço usando Nominatim
        
        Args:
            address: Endereço completo ou parcial
            city: Cidade (opcional)
            state: Estado (opcional)
            
        Returns:
            Dict com coordenadas ou erro
        """
        # Montar query de busca
        query_parts = [address]
        if city:
            query_parts.append(city)
        if state:
            query_parts.append(state)
        query_parts.append("Brasil")
        
        query = ", ".join(query_parts)
        
        # Cache key
        cache_key = f"geocode_{hash(query.lower())}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            params = {
                'q': query,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1,
                'countrycodes': 'br'  # Limitar ao Brasil
            }
            
            url = f"{cls.NOMINATIM_URL}/search"
            response = requests.get(url, params=params, headers=cls.HEADERS, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data:
                    location = data[0]
                    result = {
                        'success': True,
                        'data': {
                            'lat': float(location['lat']),
                            'lon': float(location['lon']),
                            'display_name': location.get('display_name', ''),
                            'address_details': location.get('address', {}),
                            'raw_data': location
                        }
                    }
                else:
                    result = {
                        'success': False,
                        'error': 'Endereço não encontrado'
                    }
                
                # Cache por 1 hora
                cache.set(cache_key, result, 3600)
                return result
            
            else:
                return {
                    'success': False,
                    'error': f'Erro na API de geocoding: {response.status_code}'
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao geocodificar endereço '{query}': {e}")
            return {
                'success': False,
                'error': 'Erro de conexão com o serviço de geocoding'
            }
        except Exception as e:
            logger.error(f"Erro inesperado ao geocodificar '{query}': {e}")
            return {
                'success': False,
                'error': 'Erro interno do servidor'
            }
    
    @classmethod
    def search_addresses(cls, query: str, limit: int = 5) -> Dict:
        """
        Busca endereços para autocomplete usando Nominatim
        
        Args:
            query: Texto de busca
            limit: Número máximo de resultados
            
        Returns:
            Dict com lista de endereços encontrados
        """
        if len(query) < 3:
            return {
                'success': False,
                'error': 'Query deve ter pelo menos 3 caracteres'
            }
        
        # Cache key
        cache_key = f"search_addresses_{hash(query.lower())}_{limit}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            params = {
                'q': f"{query}, Brasil",
                'format': 'json',
                'limit': limit,
                'addressdetails': 1,
                'countrycodes': 'br'
            }
            
            url = f"{cls.NOMINATIM_URL}/search"
            response = requests.get(url, params=params, headers=cls.HEADERS, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                results = []
                for item in data:
                    address = item.get('address', {})
                    results.append({
                        'display_name': item.get('display_name', ''),
                        'lat': float(item['lat']),
                        'lon': float(item['lon']),
                        'road': address.get('road', ''),
                        'neighbourhood': address.get('neighbourhood', ''),
                        'city': address.get('city', address.get('town', address.get('village', ''))),
                        'state': address.get('state', ''),
                        'postcode': address.get('postcode', ''),
                        'raw_data': item
                    })
                
                result = {
                    'success': True,
                    'data': results
                }
                
                # Cache por 30 minutos
                cache.set(cache_key, result, 1800)
                return result
            
            else:
                return {
                    'success': False,
                    'error': f'Erro na API de busca: {response.status_code}'
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar endereços com query '{query}': {e}")
            return {
                'success': False,
                'error': 'Erro de conexão com o serviço de busca'
            }
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar endereços '{query}': {e}")
            return {
                'success': False,
                'error': 'Erro interno do servidor'
            }
    
    @classmethod
    def get_full_address_data(cls, cep: str = "", address: str = "", city: str = "", state: str = "") -> Dict:
        """
        Combina busca por CEP + geocoding para obter dados completos
        
        Returns:
            Dict com endereço + coordenadas
        """
        result = {
            'success': True,
            'address_data': {},
            'coordinates': {},
            'errors': []
        }
        
        # 1. Buscar por CEP se fornecido
        if cep:
            cep_result = cls.get_address_by_cep(cep)
            if cep_result['success']:
                result['address_data'] = cep_result['data']
                # Usar dados do CEP para geocoding
                address = result['address_data']['logradouro']
                city = result['address_data']['cidade']
                state = result['address_data']['estado']
            else:
                result['errors'].append(f"CEP: {cep_result['error']}")
        
        # 2. Buscar coordenadas
        if address or city:
            geo_result = cls.get_coordinates_by_address(address, city, state)
            if geo_result['success']:
                result['coordinates'] = geo_result['data']
            else:
                result['errors'].append(f"Coordenadas: {geo_result['error']}")
        
        # 3. Verificar se tudo deu certo
        if result['errors'] and not result['address_data'] and not result['coordinates']:
            result['success'] = False
        
        return result


class BrazilianStates:
    """Classe helper com estados brasileiros"""
    
    STATES = [
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('AM', 'Amazonas'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'),
        ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PR', 'Paraná'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'),
        ('SE', 'Sergipe'),
        ('TO', 'Tocantins'),
    ]
    
    @classmethod
    def get_choices(cls):
        """Retorna choices para Django forms"""
        return [('', 'Selecione o estado...')] + cls.STATES
    
    @classmethod
    def get_state_name(cls, uf: str):
        """Retorna nome completo do estado pela sigla"""
        for code, name in cls.STATES:
            if code == uf.upper():
                return name
        return uf