from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from django.db import models
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
# Removido drf_yasg - usando apenas drf_spectacular

from users.models import User
from ads.models import Necessidade
from categories.models import Categoria, SubCategoria
from budgets.models import Orcamento
from rankings.models import Avaliacao

from .serializers import (
    UserSerializer,
    UserDetailSerializer,
    CategoriaSerializer,
    SubCategoriaSerializer,
    NecessidadeSerializer,
    NecessidadeDetailSerializer,
    OrcamentoSerializer,
    AvaliacaoSerializer,
    # Serializers para documentação
    PasswordChangeSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer,
    VersionInfoSerializer,
    NecessidadeCreateSerializer,
    OrcamentoCreateSerializer,
)
from .permissions import (
    IsOwnerOrReadOnly, 
    IsAdminOrReadOnly, 
    UserProfilePermission, 
    RestrictSensitiveFields,
    NecessidadePermission,
    OrcamentoPermission,
    AvaliacaoPermission,
    IsOwnerOrRelatedUser,
)
from .filters import UserFilter, NecessidadeFilter, OrcamentoFilter, AvaliacaoFilter
from .versions import VERSION_METADATA, CURRENT_API_VERSION, SUPPORTED_VERSIONS

from django.shortcuts import redirect
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from dj_rest_auth.views import LoginView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


@extend_schema_view(
    list=extend_schema(
        tags=['01 - USUÁRIOS - GESTÃO DE PERFIS'],
        summary="Listar usuários",
        description="Lista todos os usuários ativos do sistema. Usuários não-administradores só podem ver usuários ativos.",
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Buscar por nome, sobrenome ou email'
            ),
            OpenApiParameter(
                name='is_client',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filtrar apenas clientes'
            ),
            OpenApiParameter(
                name='is_supplier',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filtrar apenas fornecedores'
            ),
            OpenApiParameter(
                name='cidade',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filtrar por cidade'
            ),
            OpenApiParameter(
                name='estado',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filtrar por estado'
            ),
        ],
        responses={
            200: UserSerializer(many=True),
            401: OpenApiExample('Não autenticado', value={'detail': 'Authentication credentials were not provided.'}),
        }
    ),
    create=extend_schema(
        tags=['01 - USUÁRIOS - GESTÃO DE PERFIS'],
        summary="Criar usuário (não disponível)",
        description="Criação de usuários não é permitida via API. Use os endpoints de registro em /auth/registration/.",
        responses={
            405: OpenApiExample('Método não permitido', value={'error': 'Use os endpoints de registro para criar usuários'}),
        }
    ),
    retrieve=extend_schema(
        tags=['01 - USUÁRIOS - GESTÃO DE PERFIS'],
        summary="Visualizar usuário",
        description="Visualiza detalhes de um usuário específico. Usuários não-administradores só podem ver seu próprio perfil completo.",
        responses={
            200: UserDetailSerializer,
            403: OpenApiExample('Sem permissão', value={'detail': 'You do not have permission to perform this action.'}),
            404: OpenApiExample('Não encontrado', value={'detail': 'Not found.'}),
        }
    ),
    update=extend_schema(
        tags=['01 - USUÁRIOS - GESTÃO DE PERFIS'],
        summary="Atualizar usuário",
        description="Atualiza todos os dados de um usuário. Apenas o próprio usuário ou administradores podem editar.",
        request=UserDetailSerializer,
        responses={
            200: UserDetailSerializer,
            400: OpenApiExample('Dados inválidos', value={'email': ['Este e-mail já está sendo usado por outro usuário.']}),
            403: OpenApiExample('Sem permissão', value={'error': 'Você não tem permissão para modificar o campo is_staff.'}),
        }
    ),
    partial_update=extend_schema(
        tags=['01 - USUÁRIOS - GESTÃO DE PERFIS'],
        summary="Atualizar usuário parcialmente",
        description="Atualiza campos específicos de um usuário. Apenas o próprio usuário ou administradores podem editar.",
        request=UserDetailSerializer,
        responses={
            200: UserDetailSerializer,
            400: OpenApiExample('Dados inválidos', value={'email': ['Este e-mail já está sendo usado por outro usuário.']}),
            403: OpenApiExample('Sem permissão', value={'error': 'Você não tem permissão para modificar o campo is_staff.'}),
        }
    ),
    destroy=extend_schema(
        tags=['01 - USUÁRIOS - GESTÃO DE PERFIS'],
        summary="Excluir usuário",
        description="Exclui um usuário do sistema. Apenas administradores podem excluir usuários.",
        responses={
            204: None,
            403: OpenApiExample('Sem permissão', value={'detail': 'You do not have permission to perform this action.'}),
            404: OpenApiExample('Não encontrado', value={'detail': 'Not found.'}),
        }
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    01 - USUÁRIOS - GESTÃO DE PERFIS
    
    Gerenciamento completo de usuários do sistema Indicai.
    Permite visualizar, editar e gerenciar perfis de clientes e fornecedores.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserProfilePermission, RestrictSensitiveFields]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = UserFilter
    search_fields = ['first_name', 'last_name', 'email']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer

    def get_queryset(self):
        """
        Filtra usuários baseado nas permissões do usuário atual.
        """
        queryset = User.objects.all()
        
        # Usuários não-staff só podem ver usuários ativos
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
            
        # Se não for staff, só pode ver seu próprio perfil completo
        if not self.request.user.is_staff and self.action in ['retrieve', 'update', 'partial_update']:
            # Para ações específicas de um usuário, verificar se é o próprio usuário
            if hasattr(self, 'kwargs') and 'pk' in self.kwargs:
                try:
                    user_id = int(self.kwargs['pk'])
                    if user_id != self.request.user.id:
                        # Se não é o próprio usuário, retornar queryset vazio para não-staff
                        return queryset.none()
                except (ValueError, TypeError):
                    pass
        
        return queryset

    def create(self, request, *args, **kwargs):
        """Criar novo usuário (não disponível via API - use endpoints de registro)"""
        return Response({'error': 'Use os endpoints de registro para criar usuários'}, status=405)

    def perform_update(self, serializer):
        """
        Validações adicionais antes de atualizar um usuário.
        """
        # Verificar se está tentando modificar e-mail para um já existente
        if 'email' in serializer.validated_data:
            new_email = serializer.validated_data['email']
            existing_user = User.objects.filter(email=new_email).exclude(pk=self.get_object().pk).first()
            if existing_user:
                return Response(
                    {'error': 'Este e-mail já está sendo usado por outro usuário.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Impedir que usuários não-staff modifiquem campos sensíveis
        if not self.request.user.is_staff:
            sensitive_fields = ['is_staff', 'is_superuser', 'is_active', 'email_verified']
            for field in sensitive_fields:
                if field in serializer.validated_data:
                    return Response(
                        {'error': f'Você não tem permissão para modificar o campo {field}.'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
        
        serializer.save()

    @extend_schema(
        tags=['01 - USUÁRIOS - GESTÃO DE PERFIS'],
        summary="Listar avaliações recebidas",
        description="Retorna todas as avaliações que o usuário recebeu de outros usuários do sistema.",
        responses={
            200: AvaliacaoSerializer(many=True),
            404: OpenApiExample('Usuário não encontrado', value={'detail': 'Not found.'}),
        }
    )
    @action(detail=True, methods=['get'])
    def avaliacoes(self, request, pk=None):
        """
        Retorna as avaliações recebidas pelo usuário.
        """
        user = self.get_object()
        avaliacoes = Avaliacao.objects.filter(avaliado=user)
        serializer = AvaliacaoSerializer(avaliacoes, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        tags=['01 - USUÁRIOS - GESTÃO DE PERFIS'],
        summary="Listar necessidades do usuário",
        description="Retorna todas as necessidades (anúncios) que o usuário criou. Apenas o próprio usuário ou administradores podem acessar.",
        responses={
            200: NecessidadeSerializer(many=True),
            403: OpenApiExample('Sem permissão', value={'error': 'Você não tem permissão para ver as necessidades deste usuário.'}),
            404: OpenApiExample('Usuário não encontrado', value={'detail': 'Not found.'}),
        }
    )
    @action(detail=True, methods=['get'])
    def necessidades(self, request, pk=None):
        """
        Retorna as necessidades (anúncios) criados pelo usuário.
        """
        user = self.get_object()
        # Apenas o próprio usuário ou admin pode ver suas necessidades
        if request.user != user and not request.user.is_staff:
            return Response(
                {'error': 'Você não tem permissão para ver as necessidades deste usuário.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        necessidades = Necessidade.objects.filter(cliente=user)
        serializer = NecessidadeSerializer(necessidades, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        tags=['01 - USUÁRIOS - GESTÃO DE PERFIS'],
        summary="Listar orçamentos do usuário",
        description="Retorna todos os orçamentos que o usuário fez como fornecedor. Apenas o próprio usuário ou administradores podem acessar.",
        responses={
            200: OrcamentoSerializer(many=True),
            403: OpenApiExample('Sem permissão', value={'error': 'Você não tem permissão para ver os orçamentos deste usuário.'}),
            404: OpenApiExample('Usuário não encontrado', value={'detail': 'Not found.'}),
        }
    )
    @action(detail=True, methods=['get'])
    def orcamentos(self, request, pk=None):
        """
        Retorna os orçamentos feitos pelo usuário (como fornecedor).
        """
        user = self.get_object()
        # Apenas o próprio usuário ou admin pode ver seus orçamentos
        if request.user != user and not request.user.is_staff:
            return Response(
                {'error': 'Você não tem permissão para ver os orçamentos deste usuário.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        orcamentos = Orcamento.objects.filter(fornecedor=user)
        serializer = OrcamentoSerializer(orcamentos, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['01 - USUÁRIOS - GESTÃO DE PERFIS'],
        summary="Alterar senha",
        description="Permite que o usuário altere sua própria senha. Requer senha atual e nova senha com critérios de segurança.",
        request=PasswordChangeSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        examples=[
            OpenApiExample(
                'Requisição de alteração de senha',
                value={
                    'old_password': 'senha_atual_123',
                    'new_password': 'nova_senha_segura_456'
                },
                request_only=True
            ),
            OpenApiExample(
                'Senha alterada com sucesso',
                value={'message': 'Senha alterada com sucesso.'},
                response_only=True,
                status_codes=['200']
            ),
            OpenApiExample(
                'Erro de validação',
                value={'error': 'Senha atual incorreta.'},
                response_only=True,
                status_codes=['400']
            )
        ]
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request, pk=None):
        """
        Endpoint para alterar senha do usuário com validação de força.
        """
        from users.utils import validate_password_strength
        
        user = self.get_object()
        
        # Apenas o próprio usuário pode alterar sua senha
        if request.user != user:
            return Response(
                {'error': 'Você só pode alterar sua própria senha.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response(
                {'error': 'Senha atual e nova senha são obrigatórias.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.check_password(old_password):
            return Response(
                {'error': 'Senha atual incorreta.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar força da nova senha
        try:
            validate_password_strength(new_password)
        except ValidationError as e:
            return Response(
                {'error': 'Senha não atende aos critérios de segurança.', 'details': e.messages}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Senha alterada com sucesso.'})


@extend_schema_view(
    list=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
    create=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
    retrieve=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
    update=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
    partial_update=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
    destroy=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
)
class CategoriaViewSet(viewsets.ModelViewSet):
    """
    02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS
    
    Gerenciamento de categorias de produtos e serviços.
    Organiza os diferentes tipos de necessidades disponíveis no sistema.
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome', 'descricao']



    @swagger_auto_schema(
        tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS'],
        operation_summary="Listar subcategorias da categoria",
        operation_description="Retorna todas as subcategorias que pertencem a esta categoria específica.",
        responses={200: SubCategoriaSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def subcategorias(self, request, pk=None):
        """
        Retorna as subcategorias de uma categoria específica.
        """
        categoria = self.get_object()
        subcategorias = SubCategoria.objects.filter(categoria=categoria)
        serializer = SubCategoriaSerializer(subcategorias, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS'],
        operation_summary="Listar necessidades da categoria",
        operation_description="Retorna todas as necessidades (anúncios) ativas que pertencem a esta categoria.",
        responses={200: NecessidadeSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def necessidades(self, request, pk=None):
        """
        Retorna as necessidades (anúncios) de uma categoria específica.
        """
        categoria = self.get_object()
        necessidades = Necessidade.objects.filter(categoria=categoria, status='ativo')
        serializer = NecessidadeSerializer(necessidades, many=True)
        return Response(serializer.data)


class SubCategoriaViewSet(viewsets.ModelViewSet):
    """
    03 - SUBCATEGORIAS - ESPECIALIZAÇÃO DE SERVIÇOS
    
    Gerenciamento de subcategorias de produtos e serviços.
    Permite classificação mais específica das necessidades dentro de cada categoria.
    """
    queryset = SubCategoria.objects.all()
    serializer_class = SubCategoriaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['categoria']
    search_fields = ['nome', 'descricao']

    @swagger_auto_schema(tags=['03 - SUBCATEGORIAS - ESPECIALIZAÇÃO DE SERVIÇOS'])
    def list(self, request, *args, **kwargs):
        """Listar todas as subcategorias disponíveis"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['03 - SUBCATEGORIAS - ESPECIALIZAÇÃO DE SERVIÇOS'])
    def create(self, request, *args, **kwargs):
        """Criar nova subcategoria (apenas administradores)"""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['03 - SUBCATEGORIAS - ESPECIALIZAÇÃO DE SERVIÇOS'])
    def retrieve(self, request, *args, **kwargs):
        """Visualizar detalhes de uma subcategoria específica"""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['03 - SUBCATEGORIAS - ESPECIALIZAÇÃO DE SERVIÇOS'])
    def update(self, request, *args, **kwargs):
        """Atualizar subcategoria (apenas administradores)"""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['03 - SUBCATEGORIAS - ESPECIALIZAÇÃO DE SERVIÇOS'])
    def partial_update(self, request, *args, **kwargs):
        """Atualizar subcategoria parcialmente (apenas administradores)"""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['03 - SUBCATEGORIAS - ESPECIALIZAÇÃO DE SERVIÇOS'])
    def destroy(self, request, *args, **kwargs):
        """Excluir subcategoria (apenas administradores)"""
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['03 - SUBCATEGORIAS - ESPECIALIZAÇÃO DE SERVIÇOS'],
        operation_summary="Listar necessidades da subcategoria",
        operation_description="Retorna todas as necessidades (anúncios) ativas que pertencem a esta subcategoria específica.",
        responses={200: NecessidadeSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def necessidades(self, request, pk=None):
        """
        Retorna as necessidades (anúncios) de uma subcategoria específica.
        """
        subcategoria = self.get_object()
        necessidades = Necessidade.objects.filter(subcategoria=subcategoria, status='ativo')
        serializer = NecessidadeSerializer(necessidades, many=True)
        return Response(serializer.data)


class NecessidadeViewSet(viewsets.ModelViewSet):
    """
    04 - NECESSIDADES - ANÚNCIOS DE DEMANDA
    
    Gerenciamento de necessidades (anúncios) de clientes.
    Permite que clientes publiquem suas demandas por produtos ou serviços.
    """
    queryset = Necessidade.objects.all()
    serializer_class = NecessidadeSerializer
    permission_classes = [NecessidadePermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = NecessidadeFilter
    search_fields = ['titulo', 'descricao']

    @swagger_auto_schema(tags=['04 - NECESSIDADES - ANÚNCIOS DE DEMANDA'])
    def list(self, request, *args, **kwargs):
        """Listar todas as necessidades (anúncios) ativas"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['04 - NECESSIDADES - ANÚNCIOS DE DEMANDA'])
    def create(self, request, *args, **kwargs):
        """Criar nova necessidade (apenas clientes)"""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['04 - NECESSIDADES - ANÚNCIOS DE DEMANDA'])
    def retrieve(self, request, *args, **kwargs):
        """Visualizar detalhes de uma necessidade específica"""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['04 - NECESSIDADES - ANÚNCIOS DE DEMANDA'])
    def update(self, request, *args, **kwargs):
        """Atualizar necessidade (apenas o cliente que criou)"""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['04 - NECESSIDADES - ANÚNCIOS DE DEMANDA'])
    def partial_update(self, request, *args, **kwargs):
        """Atualizar necessidade parcialmente (apenas o cliente que criou)"""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['04 - NECESSIDADES - ANÚNCIOS DE DEMANDA'])
    def destroy(self, request, *args, **kwargs):
        """Excluir necessidade (apenas o cliente que criou)"""
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NecessidadeDetailSerializer
        return NecessidadeSerializer

    def get_queryset(self):
        """
        Filtra necessidades baseado nas permissões do usuário atual.
        """
        queryset = Necessidade.objects.all()
        
        # Usuários não-staff só podem ver anúncios ativos
        if not self.request.user.is_staff:
            queryset = queryset.filter(status='ativo')
            
        return queryset

    def perform_create(self, serializer):
        """
        Define o cliente como o usuário atual ao criar uma necessidade.
        """
        serializer.save(cliente=self.request.user)

    @swagger_auto_schema(
        tags=['04 - NECESSIDADES - ANÚNCIOS DE DEMANDA'],
        operation_summary="Listar orçamentos da necessidade",
        operation_description="Retorna todos os orçamentos recebidos para esta necessidade. Apenas o cliente que criou o anúncio pode visualizar.",
        responses={200: OrcamentoSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def orcamentos(self, request, pk=None):
        """
        Retorna os orçamentos de uma necessidade (anúncio) específica.
        """
        necessidade = self.get_object()
        
        # Apenas o cliente do anúncio pode ver todos os orçamentos
        if necessidade.cliente != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Você não tem permissão para ver os orçamentos deste anúncio.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        orcamentos = Orcamento.objects.filter(anuncio=necessidade)
        serializer = OrcamentoSerializer(orcamentos, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['04 - NECESSIDADES - ANÚNCIOS DE DEMANDA'],
        operation_summary="Listar avaliações da necessidade",
        operation_description="Retorna todas as avaliações relacionadas a esta necessidade específica.",
        responses={200: AvaliacaoSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def avaliacoes(self, request, pk=None):
        """
        Retorna as avaliações de uma necessidade (anúncio) específica.
        """
        necessidade = self.get_object()
        avaliacoes = Avaliacao.objects.filter(anuncio=necessidade)
        serializer = AvaliacaoSerializer(avaliacoes, many=True)
        return Response(serializer.data)


class OrcamentoViewSet(viewsets.ModelViewSet):
    """
    05 - ORÇAMENTOS - PROPOSTAS DE FORNECEDORES
    
    Gerenciamento de orçamentos enviados por fornecedores.
    Permite que fornecedores enviem propostas para as necessidades dos clientes.
    """
    queryset = Orcamento.objects.all()
    serializer_class = OrcamentoSerializer
    permission_classes = [OrcamentoPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = OrcamentoFilter
    search_fields = ['descricao']

    @swagger_auto_schema(tags=['05 - ORÇAMENTOS - PROPOSTAS DE FORNECEDORES'])
    def list(self, request, *args, **kwargs):
        """Listar orçamentos (apenas os relacionados ao usuário)"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['05 - ORÇAMENTOS - PROPOSTAS DE FORNECEDORES'])
    def create(self, request, *args, **kwargs):
        """Criar novo orçamento (apenas fornecedores)"""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['05 - ORÇAMENTOS - PROPOSTAS DE FORNECEDORES'])
    def retrieve(self, request, *args, **kwargs):
        """Visualizar detalhes de um orçamento específico"""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['05 - ORÇAMENTOS - PROPOSTAS DE FORNECEDORES'])
    def update(self, request, *args, **kwargs):
        """Atualizar orçamento (apenas o fornecedor que criou)"""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['05 - ORÇAMENTOS - PROPOSTAS DE FORNECEDORES'])
    def partial_update(self, request, *args, **kwargs):
        """Atualizar orçamento parcialmente (apenas o fornecedor que criou)"""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['05 - ORÇAMENTOS - PROPOSTAS DE FORNECEDORES'])
    def destroy(self, request, *args, **kwargs):
        """Excluir orçamento (apenas o fornecedor que criou)"""
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """
        Filtra orçamentos baseado nas permissões do usuário atual.
        """
        queryset = Orcamento.objects.all()
        
        # Usuários não-staff só podem ver seus próprios orçamentos ou orçamentos para seus anúncios
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                models.Q(fornecedor=self.request.user) |
                models.Q(anuncio__cliente=self.request.user)
            ).distinct()
            
        return queryset

    def perform_create(self, serializer):
        """
        Define o fornecedor como o usuário atual ao criar um orçamento.
        """
        serializer.save(fornecedor=self.request.user)


class AvaliacaoViewSet(viewsets.ModelViewSet):
    """
    06 - AVALIAÇÕES - SISTEMA DE REPUTAÇÃO
    
    Gerenciamento de avaliações entre usuários.
    Permite que clientes e fornecedores se avaliem mutuamente após negociações.
    """
    queryset = Avaliacao.objects.all()
    serializer_class = AvaliacaoSerializer
    permission_classes = [AvaliacaoPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AvaliacaoFilter

    @swagger_auto_schema(tags=['06 - AVALIAÇÕES - SISTEMA DE REPUTAÇÃO'])
    def list(self, request, *args, **kwargs):
        """Listar todas as avaliações públicas"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['06 - AVALIAÇÕES - SISTEMA DE REPUTAÇÃO'])
    def create(self, request, *args, **kwargs):
        """Criar nova avaliação"""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['06 - AVALIAÇÕES - SISTEMA DE REPUTAÇÃO'])
    def retrieve(self, request, *args, **kwargs):
        """Visualizar detalhes de uma avaliação específica"""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['06 - AVALIAÇÕES - SISTEMA DE REPUTAÇÃO'])
    def update(self, request, *args, **kwargs):
        """Atualizar avaliação (apenas quem criou)"""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['06 - AVALIAÇÕES - SISTEMA DE REPUTAÇÃO'])
    def partial_update(self, request, *args, **kwargs):
        """Atualizar avaliação parcialmente (apenas quem criou)"""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['06 - AVALIAÇÕES - SISTEMA DE REPUTAÇÃO'])
    def destroy(self, request, *args, **kwargs):
        """Excluir avaliação (apenas administradores)"""
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Define o usuário como o usuário atual ao criar uma avaliação.
        """
        serializer.save(usuario=self.request.user)


@extend_schema(
    tags=['00 - SISTEMA - INFORMAÇÕES GERAIS'],
    summary="Informações sobre versões da API",
    description="Retorna informações detalhadas sobre as versões disponíveis da API, incluindo recursos e status de cada versão.",
    parameters=[
        OpenApiParameter(
            name='version',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Versão específica da API (ex: v1)',
            required=False
        )
    ],
    responses={
        200: VersionInfoSerializer,
        404: OpenApiExample('Versão não encontrada', value={'error': 'Versão v2 não encontrada'}),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_version_info(request, version=None):
    """
    Endpoint para obter informações sobre versões da API.
    
    Se uma versão específica for fornecida, retorna informações sobre ela.
    Caso contrário, retorna informações sobre todas as versões suportadas.
    """
    if version:
        if version in VERSION_METADATA:
            return Response({
                'version': version,
                **VERSION_METADATA[version]
            })
        else:
            return Response(
                {'error': f'Versão {version} não encontrada'},
                status=404
            )
    
    # Retorna informações sobre todas as versões
    return Response({
        'current_version': CURRENT_API_VERSION,
        'supported_versions': SUPPORTED_VERSIONS,
        'versions': VERSION_METADATA
    }) 


@extend_schema(exclude=True)  # Excluir da documentação
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_logout_redirect(request):
    """
    View para redirecionar logout do DRF para a página inicial
    """
    if request.user.is_authenticated:
        logout(request)
    
    # Se veio do Swagger, redirecionar de volta
    next_url = request.GET.get('next', '/')
    if 'swagger' in next_url or 'api' in next_url:
        return redirect('/api/v1/swagger/')
    
    return redirect('/') 


from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.openapi import OpenApiTypes
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

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
        description='Autentica o usuário e retorna tokens JWT para acesso à API.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                        'format': 'email',
                        'description': 'E-mail do usuário'
                    },
                    'password': {
                        'type': 'string',
                        'format': 'password',
                        'description': 'Senha do usuário'
                    }
                },
                'required': ['email', 'password'],
                'example': {
                    'email': 'usuario@exemplo.com',
                    'password': 'minha_senha_123'
                }
            }
        },
        examples=[
            OpenApiExample(
                'Login Example',
                value={
                    'email': 'usuario@exemplo.com',
                    'password': 'minha_senha_123'
                },
                request_only=True,
            ),
        ],
        responses={
            200: {
                'description': 'Login realizado com sucesso',
                'content': {
                    'application/json': {
                        'example': {
                            'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                            'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                            'user': {
                                'id': 1,
                                'email': 'usuario@exemplo.com',
                                'first_name': 'João',
                                'last_name': 'Silva',
                                'tipo_usuario': 'cliente'
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Dados inválidos',
                'content': {
                    'application/json': {
                        'example': {
                            'error': 'Email e senha são obrigatórios'
                        }
                    }
                }
            },
            401: {
                'description': 'Credenciais inválidas',
                'content': {
                    'application/json': {
                        'example': {
                            'error': 'Credenciais inválidas'
                        }
                    }
                }
            }
        }
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

    def post(self, request):
        """
        Endpoint de login que aceita email e senha
        """
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'error': 'Email e senha são obrigatórios'
            }, status=400)
        
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

# Manter a função para compatibilidade
custom_login = CustomLoginView.as_view() 