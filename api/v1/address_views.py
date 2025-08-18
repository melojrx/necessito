"""
API views para serviços de endereçamento
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from core.services.address_service import AddressService, BrazilianStates
import json


@extend_schema(
    tags=['07 - ENDEREÇOS - GEOLOCALIZAÇÃO'],
    summary="Buscar endereço por CEP",
    parameters=[
        OpenApiParameter(
            name='cep',
            location=OpenApiParameter.QUERY,
            type=OpenApiTypes.STR,
            description='CEP a ser consultado (formato: 12345-678 ou 12345678)',
            examples=[
                OpenApiExample(
                    'CEP válido',
                    value='01310-100'
                )
            ]
        )
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean'},
                'data': {
                    'type': 'object',
                    'properties': {
                        'cep': {'type': 'string'},
                        'logradouro': {'type': 'string'},
                        'bairro': {'type': 'string'},
                        'cidade': {'type': 'string'},
                        'estado': {'type': 'string'},
                        'uf': {'type': 'string'}
                    }
                }
            }
        },
        400: {'description': 'CEP não informado'},
        404: {'description': 'CEP não encontrado'}
    }
)
@api_view(['GET'])
@permission_classes([])  # Permitir acesso público para busca de CEP
def search_cep(request):
    """
    Busca endereço por CEP
    GET /api/v1/address/cep/{cep}/
    """
    cep = request.GET.get('cep', '').strip()
    
    if not cep:
        return Response({
            'success': False,
            'error': 'CEP é obrigatório'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    result = AddressService.get_address_by_cep(cep)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([])  # Permitir acesso público
def search_addresses(request):
    """
    Busca endereços para autocomplete
    GET /api/v1/address/search/?q=termo&limit=5
    """
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 5))
    
    if not query:
        return Response({
            'success': False,
            'error': 'Parâmetro "q" é obrigatório'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if limit > 10:
        limit = 10  # Limitar para evitar sobrecarga
    
    result = AddressService.search_addresses(query, limit)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([])  # Permitir acesso público
def geocode_address(request):
    """
    Obtém coordenadas de um endereço
    POST /api/v1/address/geocode/
    Body: {
        "address": "Rua das Flores, 123",
        "city": "São Paulo",
        "state": "SP"
    }
    """
    data = request.data
    
    address = data.get('address', '').strip()
    city = data.get('city', '').strip()
    state = data.get('state', '').strip()
    
    if not (address or city):
        return Response({
            'success': False,
            'error': 'Endereço ou cidade são obrigatórios'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    result = AddressService.get_coordinates_by_address(address, city, state)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([])  # Permitir acesso público
def get_states(request):
    """
    Retorna lista de estados brasileiros
    GET /api/v1/address/states/
    """
    return Response({
        'success': True,
        'data': [
            {'code': code, 'name': name}
            for code, name in BrazilianStates.STATES
        ]
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_address(request):
    """
    Retorna endereço do usuário logado
    GET /api/v1/address/user/
    """
    user = request.user
    
    return Response({
        'success': True,
        'data': {
            'endereco': user.endereco or '',
            'bairro': user.bairro or '',
            'cep': user.cep or '',
            'cidade': user.cidade or '',
            'estado': user.estado or '',
            'lat': user.lat,
            'lon': user.lon,
        }
    }, status=status.HTTP_200_OK)


# ========== VIEWS PARA DJANGO (não DRF) ==========

@csrf_exempt
@require_http_methods(["GET"])
def django_search_cep(request):
    """View Django para busca de CEP (para usar em forms)"""
    cep = request.GET.get('cep', '').strip()
    
    if not cep:
        return JsonResponse({
            'success': False,
            'error': 'CEP é obrigatório'
        }, status=400)
    
    result = AddressService.get_address_by_cep(cep)
    return JsonResponse(result)


@csrf_exempt  
@require_http_methods(["GET"])
def django_search_addresses(request):
    """View Django para autocomplete de endereços"""
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 5))
    
    if not query:
        return JsonResponse({
            'success': False,
            'error': 'Parâmetro "q" é obrigatório'
        }, status=400)
    
    if limit > 10:
        limit = 10
    
    result = AddressService.search_addresses(query, limit)
    return JsonResponse(result)


@csrf_exempt
@require_http_methods(["POST"])
def django_geocode_address(request):
    """View Django para geocoding"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    
    address = data.get('address', '').strip()
    city = data.get('city', '').strip()  
    state = data.get('state', '').strip()
    
    if not (address or city):
        return JsonResponse({
            'success': False,
            'error': 'Endereço ou cidade são obrigatórios'
        }, status=400)
    
    result = AddressService.get_coordinates_by_address(address, city, state)
    return JsonResponse(result)