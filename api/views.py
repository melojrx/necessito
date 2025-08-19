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


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet base com configurações comuns para a API Indicai.
    """
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    def get_queryset(self):
        """
        Filtragem padrão para usuários não-staff.
        Override em classes filhas para filtros específicos.
        """
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = self._filter_for_regular_user(queryset)
        return queryset
    
    def _filter_for_regular_user(self, queryset):
        """
        Método a ser sobrescrito pelas classes filhas para aplicar
        filtros específicos para usuários não-staff.
        """
        return queryset

@extend_schema_view(
    list=extend_schema(tags=['01 - USUÁRIOS - GESTÃO DE PERFIS']),
    create=extend_schema(tags=['01 - USUÁRIOS - GESTÃO DE PERFIS']),
    retrieve=extend_schema(tags=['01 - USUÁRIOS - GESTÃO DE PERFIS']),
    update=extend_schema(tags=['01 - USUÁRIOS - GESTÃO DE PERFIS']),
    partial_update=extend_schema(tags=['01 - USUÁRIOS - GESTÃO DE PERFIS']),
    destroy=extend_schema(tags=['01 - USUÁRIOS - GESTÃO DE PERFIS']),
)
class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_client', 'is_supplier', 'cidade', 'estado']
    search_fields = ['first_name', 'last_name', 'email']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer

    def _filter_for_regular_user(self, queryset):
        return queryset.filter(is_active=True)

@extend_schema_view(
    list=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
    create=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
    retrieve=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
    update=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
    partial_update=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
    destroy=extend_schema(tags=['02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS']),
)
class CategoriaViewSet(BaseModelViewSet):
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
class SubCategoriaViewSet(BaseModelViewSet):
    queryset = SubCategoria.objects.all()
    serializer_class = SubCategoriaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
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
class NecessidadeViewSet(BaseModelViewSet):
    queryset = Necessidade.objects.all()
    serializer_class = NecessidadeSerializer
    permission_classes = [NecessidadePermission]
    filterset_class = NecessidadeFilter
    search_fields = ['titulo', 'descricao']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NecessidadeDetailSerializer
        return NecessidadeSerializer

    def _filter_for_regular_user(self, queryset):
        return queryset.filter(status='ativo')

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
class OrcamentoViewSet(BaseModelViewSet):
    queryset = Orcamento.objects.all()
    serializer_class = OrcamentoSerializer
    permission_classes = [OrcamentoPermission]
    filterset_class = OrcamentoFilter
    search_fields = ['descricao']

    def _filter_for_regular_user(self, queryset):
        return queryset.filter(
            models.Q(fornecedor=self.request.user) |
            models.Q(anuncio__cliente=self.request.user)
        ).distinct()

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
class AvaliacaoViewSet(BaseModelViewSet):
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