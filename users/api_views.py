from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from core.services.address_service import AddressService
import json

@method_decorator(csrf_exempt, name='dispatch')
class ConsultaCepView(View):
    """
    API endpoint para consulta de CEP usando ViaCEP
    """
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            cep = data.get('cep', '').strip()
            
            if not cep:
                return JsonResponse({
                    'success': False,
                    'error': 'CEP é obrigatório'
                }, status=400)
            
            # Usar o serviço existente
            result = AddressService.get_address_by_cep(cep)
            
            if result['success']:
                # Retornar apenas os campos necessários
                address_data = result['data']
                return JsonResponse({
                    'success': True,
                    'data': {
                        'cep': address_data.get('cep', ''),
                        'logradouro': address_data.get('logradouro', ''),
                        'bairro': address_data.get('bairro', ''),
                        'cidade': address_data.get('cidade', ''),
                        'estado': address_data.get('estado', ''),
                        'complemento': address_data.get('complemento', ''),
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result.get('error', 'Erro desconhecido')
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON inválido'
            }, status=400)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': 'Erro interno do servidor'
            }, status=500)
    
    def get(self, request):
        """Método GET não permitido"""
        return JsonResponse({
            'success': False,
            'error': 'Método não permitido. Use POST.'
        }, status=405)
