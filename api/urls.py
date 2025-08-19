from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from .views import (
    UserViewSet,
    CategoriaViewSet,
    SubCategoriaViewSet,
    NecessidadeViewSet,
    OrcamentoViewSet,
    AvaliacaoViewSet,
    api_version_info,
    api_logout_redirect,
)
from .auth_views import CustomLoginView
from .v1.address_views import (
    search_cep, search_addresses, geocode_address, 
    get_states, get_user_address,
    django_search_cep, django_search_addresses, django_geocode_address
)

# Configuração do router para v1
v1_router = DefaultRouter()
v1_router.register(r'users', UserViewSet)
v1_router.register(r'categorias', CategoriaViewSet)
v1_router.register(r'subcategorias', SubCategoriaViewSet)
v1_router.register(r'necessidades', NecessidadeViewSet)
v1_router.register(r'orcamentos', OrcamentoViewSet)
v1_router.register(r'avaliacoes', AvaliacaoViewSet)

# URLs da API versionada
v1_urlpatterns = [
    # Endpoints da API v1
    path('', include(v1_router.urls)),
    
    # Autenticação customizada - endpoints principais
    path('auth/login/', CustomLoginView.as_view(), name='auth-login'),
    
    # Outros endpoints de autenticação do dj-rest-auth (exceto login para evitar duplicação)
    path('auth/logout/', include('dj_rest_auth.urls')),
    path('auth/password/change/', include('dj_rest_auth.urls')),
    path('auth/password/reset/', include('dj_rest_auth.urls')),
    path('auth/user/', include('dj_rest_auth.urls')),
    
    # Registro de usuários
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    
    # ==================== ENDPOINTS DE ENDEREÇAMENTO ====================
    # API REST (DRF)
    path('address/cep/', search_cep, name='api-search-cep'),
    path('address/search/', search_addresses, name='api-search-addresses'),
    path('address/geocode/', geocode_address, name='api-geocode-address'),
    path('address/states/', get_states, name='api-get-states'),
    path('address/user/', get_user_address, name='api-get-user-address'),
]

# URLs principais da API
urlpatterns = [
    # Endpoint de informações de versão (sem versionamento)
    path('version/', api_version_info, name='api-version-info'),
    path('version/<str:version>/', api_version_info, name='api-version-detail'),
    
    # Logout redirect para corrigir problema do DRF
    path('logout-redirect/', api_logout_redirect, name='api-logout-redirect'),
    
    # API v1 (versão atual) - APENAS esta versão aparecerá no Swagger
    path('v1/', include(v1_urlpatterns)),
    
    # ==================== ENDPOINTS DJANGO (para formulários) ====================
    path('django/address/cep/', django_search_cep, name='django-search-cep'),
    path('django/address/search/', django_search_addresses, name='django-search-addresses'),
    path('django/address/geocode/', django_geocode_address, name='django-geocode-address'),
    
    # URLs do DRF Spectacular - Documentação da API
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui-alt'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] 