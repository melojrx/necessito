import django_filters
from users.models import User
from ads.models import Necessidade
from budgets.models import Orcamento
from rankings.models import Avaliacao


class UserFilter(django_filters.FilterSet):
    """
    Filtros personalizados para o modelo User.
    """
    nome = django_filters.CharFilter(method='filter_nome')
    
    class Meta:
        model = User
        fields = {
            'is_client': ['exact'],
            'is_supplier': ['exact'],
            'cidade': ['exact', 'icontains'],
            'estado': ['exact'],
            'date_joined': ['gte', 'lte'],
        }
    
    def filter_nome(self, queryset, name, value):
        """
        Filtra por nome completo (first_name + last_name).
        """
        return queryset.filter(first_name__icontains=value) | queryset.filter(last_name__icontains=value)


class NecessidadeFilter(django_filters.FilterSet):
    """
    Filtros personalizados para o modelo Necessidade.
    """
    preco_min = django_filters.NumberFilter(field_name='valor', lookup_expr='gte')
    preco_max = django_filters.NumberFilter(field_name='valor', lookup_expr='lte')
    data_min = django_filters.DateFilter(field_name='data_criacao', lookup_expr='gte')
    data_max = django_filters.DateFilter(field_name='data_criacao', lookup_expr='lte')
    
    class Meta:
        model = Necessidade
        fields = {
            'cliente': ['exact'],
            'categoria': ['exact'],
            'subcategoria': ['exact'],
            'status': ['exact'],
            'titulo': ['icontains'],
            'descricao': ['icontains'],
        }


class OrcamentoFilter(django_filters.FilterSet):
    """
    Filtros personalizados para o modelo Orcamento.
    """
    valor_min = django_filters.NumberFilter(field_name='valor', lookup_expr='gte')
    valor_max = django_filters.NumberFilter(field_name='valor', lookup_expr='lte')
    
    class Meta:
        model = Orcamento
        fields = {
            'fornecedor': ['exact'],
            'anuncio': ['exact'],
            'status': ['exact'],
            'data_criacao': ['gte', 'lte'],
        }


class AvaliacaoFilter(django_filters.FilterSet):
    """
    Filtros personalizados para o modelo Avaliacao.
    """
    estrelas_min = django_filters.NumberFilter(field_name='media_estrelas', lookup_expr='gte')
    estrelas_max = django_filters.NumberFilter(field_name='media_estrelas', lookup_expr='lte')
    
    class Meta:
        model = Avaliacao
        fields = {
            'usuario': ['exact'],
            'avaliado': ['exact'],
            'anuncio': ['exact'],
            'tipo_avaliacao': ['exact'],
            'data_avaliacao': ['gte', 'lte'],
        } 