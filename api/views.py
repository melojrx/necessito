from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import logout
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from users.models import User
from ads.models import Necessidade
from categories.models import Categoria, SubCategoria
from budgets.models import Orcamento
from rankings.models import Avaliacao

from .serializers import (
    UserSerializer, UserDetailSerializer,
    CategoriaSerializer, SubCategoriaSerializer,
    NecessidadeSerializer, NecessidadeDetailSerializer,
    OrcamentoSerializer, AvaliacaoSerializer,
    PasswordChangeSerializer, ErrorResponseSerializer, SuccessResponseSerializer,
    VersionInfoSerializer
)
from .permissions import (
    IsAdminOrReadOnly, NecessidadePermission, OrcamentoPermission, AvaliacaoPermission
)
from .filters import NecessidadeFilter, OrcamentoFilter, AvaliacaoFilter
from .versions import CURRENT_API_VERSION, SUPPORTED_VERSIONS, VERSION_METADATA

# ViewSets simplificados sem decoradores drf_yasg

@extend_schema_view(
    list=extend_schema(tags=['01 - USUÁRIOS - GESTÃO DE PERFIS']),
    create=extend_schema(tags=['01 - USUÁRIOS - GESTÃO DE PERFIS']),
    retrieve=extend_schema(tags=['01 - USUÁRIOS - GESTÃO DE PERFIS']),
    update=extend_schema(tags=['01 - USUÁRIOS - GESTÃO DE PERFIS']),
    partial_update=extend_schema(tags=['01 - USUÁRIOS - GESTÃO DE PERFIS']),
    destroy=extend_schema(tags=['01 - USUÁRIOS - GESTÃO DE PERFIS']),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_client', 'is_supplier', 'cidade', 'estado']
    search_fields = ['first_name', 'last_name', 'email']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset

@extend_schema_view(
    list=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
    create=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
    retrieve=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
    update=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
    partial_update=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
    destroy=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
)
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome', 'descricao']

@extend_schema_view(
    list=extend_schema(tags=['03 - SUBCATEGORIAS - ESPECIALIZAÇÃO DE SERVIÇOS']),
    create=extend_schema(tags=['03 - SUBCATEGORIAS - ESPECIALIZAÇÃO DE SERVIÇOS']),
    retrieve=extend_schema(tags=['03 - SUBCATEGORIAS - ESPECIALIZAÇÃO DE SERVIÇOS']),
    update=extend_schema(tags=['03 - SUBCATEGORIAS - ESPECIALIZAÇÃO DE SERVIÇOS']),
    partial_update=extend_schema(tags=['03 - SUBCATEGORIAS - ESPECIALIZAÇÃO DE SERVIÇOS']),
    destroy=extend_schema(tags=['03 - SUBCATEGORIAS - ESPECIALIZAÇÃO DE SERVIÇOS']),
)
class SubCategoriaViewSet(viewsets.ModelViewSet):
    queryset = SubCategoria.objects.all()
    serializer_class = SubCategoriaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['categoria']
    search_fields = ['nome', 'descricao']

@extend_schema_view(
    list=extend_schema(tags=['04 - NECESSIDADES - ANÚNCIOS DE DEMANDA']),
    create=extend_schema(tags=['04 - NECESSIDADES - ANÚNCIOS DE DEMANDA']),
    retrieve=extend_schema(tags=['04 - NECESSIDADES - ANÚNCIOS DE DEMANDA']),
    update=extend_schema(tags=['04 - NECESSIDADES - ANÚNCIOS DE DEMANDA']),
    partial_update=extend_schema(tags=['04 - NECESSIDADES - ANÚNCIOS DE DEMANDA']),
    destroy=extend_schema(tags=['04 - NECESSIDADES - ANÚNCIOS DE DEMANDA']),
)
class NecessidadeViewSet(viewsets.ModelViewSet):
    queryset = Necessidade.objects.all()
    serializer_class = NecessidadeSerializer
    permission_classes = [NecessidadePermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = NecessidadeFilter
    search_fields = ['titulo', 'descricao']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NecessidadeDetailSerializer
        return NecessidadeSerializer

    def get_queryset(self):
        queryset = Necessidade.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(status='ativo')
        return queryset

    def perform_create(self, serializer):
        serializer.save(cliente=self.request.user)

@extend_schema_view(
    list=extend_schema(tags=['05 - ORÇAMENTOS - PROPOSTAS DE FORNECEDORES']),
    create=extend_schema(tags=['05 - ORÇAMENTOS - PROPOSTAS DE FORNECEDORES']),
    retrieve=extend_schema(tags=['05 - ORÇAMENTOS - PROPOSTAS DE FORNECEDORES']),
    update=extend_schema(tags=['05 - ORÇAMENTOS - PROPOSTAS DE FORNECEDORES']),
    partial_update=extend_schema(tags=['05 - ORÇAMENTOS - PROPOSTAS DE FORNECEDORES']),
    destroy=extend_schema(tags=['05 - ORÇAMENTOS - PROPOSTAS DE FORNECEDORES']),
)
class OrcamentoViewSet(viewsets.ModelViewSet):
    queryset = Orcamento.objects.all()
    serializer_class = OrcamentoSerializer
    permission_classes = [OrcamentoPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = OrcamentoFilter
    search_fields = ['descricao']

    def get_queryset(self):
        queryset = Orcamento.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                models.Q(fornecedor=self.request.user) |
                models.Q(anuncio__cliente=self.request.user)
            ).distinct()
        return queryset

    def perform_create(self, serializer):
        serializer.save(fornecedor=self.request.user)

@extend_schema_view(
    list=extend_schema(tags=['06 - AVALIAÇÕES - SISTEMA DE REPUTAÇÃO']),
    create=extend_schema(tags=['06 - AVALIAÇÕES - SISTEMA DE REPUTAÇÃO']),
    retrieve=extend_schema(tags=['06 - AVALIAÇÕES - SISTEMA DE REPUTAÇÃO']),
    update=extend_schema(tags=['06 - AVALIAÇÕES - SISTEMA DE REPUTAÇÃO']),
    partial_update=extend_schema(tags=['06 - AVALIAÇÕES - SISTEMA DE REPUTAÇÃO']),
    destroy=extend_schema(tags=['06 - AVALIAÇÕES - SISTEMA DE REPUTAÇÃO']),
)
class AvaliacaoViewSet(viewsets.ModelViewSet):
    queryset = Avaliacao.objects.all()
    serializer_class = AvaliacaoSerializer
    permission_classes = [AvaliacaoPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AvaliacaoFilter

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

@extend_schema(
    tags=['00 - SISTEMA - INFORMAÇÕES GERAIS'],
    summary="Informações sobre versões da API",
)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_version_info(request, version=None):
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
    
    return Response({
        'current_version': CURRENT_API_VERSION,
        'supported_versions': SUPPORTED_VERSIONS,
        'versions': VERSION_METADATA
    })

@extend_schema(exclude=True)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_logout_redirect(request):
    if request.user.is_authenticated:
        logout(request)
    
    next_url = request.GET.get('next', '/')
    if 'swagger' in next_url or 'api' in next_url:
        return redirect('/api/v1/swagger/')
    
    return redirect('/') 