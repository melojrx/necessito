from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

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
)
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from .filters import UserFilter, NecessidadeFilter, OrcamentoFilter, AvaliacaoFilter


class UserViewSet(viewsets.ModelViewSet):
    """
    API para gerenciamento de usuários.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = UserFilter
    search_fields = ['first_name', 'last_name', 'email']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        return UserSerializer

    @action(detail=True, methods=['get'])
    def avaliacoes(self, request, pk=None):
        """
        Retorna as avaliações recebidas pelo usuário.
        """
        user = self.get_object()
        avaliacoes = Avaliacao.objects.filter(avaliado=user)
        serializer = AvaliacaoSerializer(avaliacoes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def necessidades(self, request, pk=None):
        """
        Retorna as necessidades (anúncios) criados pelo usuário.
        """
        user = self.get_object()
        necessidades = Necessidade.objects.filter(cliente=user)
        serializer = NecessidadeSerializer(necessidades, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def orcamentos(self, request, pk=None):
        """
        Retorna os orçamentos feitos pelo usuário (como fornecedor).
        """
        user = self.get_object()
        orcamentos = Orcamento.objects.filter(fornecedor=user)
        serializer = OrcamentoSerializer(orcamentos, many=True)
        return Response(serializer.data)


class CategoriaViewSet(viewsets.ModelViewSet):
    """
    API para gerenciamento de categorias.
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome', 'descricao']

    @action(detail=True, methods=['get'])
    def subcategorias(self, request, pk=None):
        """
        Retorna as subcategorias de uma categoria específica.
        """
        categoria = self.get_object()
        subcategorias = SubCategoria.objects.filter(categoria=categoria)
        serializer = SubCategoriaSerializer(subcategorias, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def necessidades(self, request, pk=None):
        """
        Retorna as necessidades (anúncios) de uma categoria específica.
        """
        categoria = self.get_object()
        necessidades = Necessidade.objects.filter(categoria=categoria)
        serializer = NecessidadeSerializer(necessidades, many=True)
        return Response(serializer.data)


class SubCategoriaViewSet(viewsets.ModelViewSet):
    """
    API para gerenciamento de subcategorias.
    """
    queryset = SubCategoria.objects.all()
    serializer_class = SubCategoriaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['categoria']
    search_fields = ['nome', 'descricao']

    @action(detail=True, methods=['get'])
    def necessidades(self, request, pk=None):
        """
        Retorna as necessidades (anúncios) de uma subcategoria específica.
        """
        subcategoria = self.get_object()
        necessidades = Necessidade.objects.filter(subcategoria=subcategoria)
        serializer = NecessidadeSerializer(necessidades, many=True)
        return Response(serializer.data)


class NecessidadeViewSet(viewsets.ModelViewSet):
    """
    API para gerenciamento de necessidades (anúncios).
    """
    queryset = Necessidade.objects.all()
    serializer_class = NecessidadeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = NecessidadeFilter
    search_fields = ['titulo', 'descricao']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NecessidadeDetailSerializer
        return NecessidadeSerializer

    @action(detail=True, methods=['get'])
    def orcamentos(self, request, pk=None):
        """
        Retorna os orçamentos de uma necessidade (anúncio) específica.
        """
        necessidade = self.get_object()
        orcamentos = Orcamento.objects.filter(anuncio=necessidade)
        serializer = OrcamentoSerializer(orcamentos, many=True)
        return Response(serializer.data)

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
    API para gerenciamento de orçamentos.
    """
    queryset = Orcamento.objects.all()
    serializer_class = OrcamentoSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = OrcamentoFilter
    search_fields = ['descricao']


class AvaliacaoViewSet(viewsets.ModelViewSet):
    """
    API para gerenciamento de avaliações.
    """
    queryset = Avaliacao.objects.all()
    serializer_class = AvaliacaoSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AvaliacaoFilter 