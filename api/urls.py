from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    CategoriaViewSet,
    SubCategoriaViewSet,
    NecessidadeViewSet,
    OrcamentoViewSet,
    AvaliacaoViewSet,
)
from .swagger import swagger_urlpatterns

# Configuração do router
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'subcategorias', SubCategoriaViewSet)
router.register(r'necessidades', NecessidadeViewSet)
router.register(r'orcamentos', OrcamentoViewSet)
router.register(r'avaliacoes', AvaliacaoViewSet)

# URLs da API
urlpatterns = [
    # Endpoints da API
    path('', include(router.urls)),
    
    # URLs de autenticação do DRF
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Adicionar URLs do Swagger
urlpatterns += swagger_urlpatterns 