from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import LoginRequestSerializer, LoginResponseSerializer, ErrorResponseSerializer

@method_decorator(csrf_exempt, name='dispatch')
class CustomLoginView(APIView):
    """
    Endpoint customizado de login para resolver problemas de CORS
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # Sem autenticação para login

    @extend_schema(
        tags=['07 - AUTENTICAÇÃO - ACESSO AO SISTEMA'],
        summary='Login de usuário',
        description='''
        Autentica o usuário e retorna tokens JWT para acesso à API.
        
        **Como usar:**
        1. Envie email e senha no corpo da requisição
        2. Receba os tokens JWT na resposta
        3. Use o token de acesso para autenticar outras requisições
        4. O token de acesso é válido por 1 hora
        5. Use o token de refresh para renovar o acesso quando necessário
        
        **Exemplo de uso no cabeçalho:**
        ```
        Authorization: Bearer {seu_token_de_acesso}
        ```
        ''',
        request=LoginRequestSerializer,
        responses={
            200: LoginResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Login Exemplo',
                summary='Exemplo de login com sucesso',
                description='Dados de exemplo para realizar login',
                value={
                    'email': 'usuario@exemplo.com',
                    'password': 'minha_senha_123'
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        """
        Endpoint de login que aceita email e senha
        """
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            response = Response({
                'error': 'Email e senha são obrigatórios'
            }, status=400)
            response['Access-Control-Allow-Origin'] = '*'
            return response
        
        user = authenticate(request, email=email, password=password)
        
        if user:
            if not user.is_active:
                response = Response({
                    'error': 'Conta de usuário está desabilitada'
                }, status=400)
                response['Access-Control-Allow-Origin'] = '*'
                return response
            
            # Gerar tokens JWT
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            
            response = Response({
                'access': str(access),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'tipo_usuario': 'cliente' if user.is_client else 'fornecedor'
                }
            })
            response['Access-Control-Allow-Origin'] = '*'
            return response
        else:
            response = Response({
                'error': 'Credenciais inválidas'
            }, status=401)
            response['Access-Control-Allow-Origin'] = '*'
            return response

    @extend_schema(
        tags=['07 - AUTENTICAÇÃO - ACESSO AO SISTEMA'],
        summary='Preflight OPTIONS para CORS',
        description='Responde às requisições OPTIONS para suporte a CORS',
        responses={200: None}
    )
    def options(self, request, *args, **kwargs):
        """
        Handle preflight OPTIONS request for CORS
        """
        response = Response()
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

# Manter a função para compatibilidade
custom_login = CustomLoginView.as_view() 