from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path

# Configuração do Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="API Necessito",
        default_version='v1',
        description="""
        API de integração do sistema Necessito.
        
        Esta API fornece acesso às principais funcionalidades do sistema, incluindo:
        - Gerenciamento de usuários
        - Categorias e subcategorias
        - Anúncios (necessidades)
        - Orçamentos
        - Avaliações
        
        A API segue os princípios REST e utiliza JSON para formatação de dados.
        """,
        terms_of_service="https://www.necessito.com.br/termos/",
        contact=openapi.Contact(email="contato@necessito.com.br"),
        license=openapi.License(name="Licença Proprietária"),
    ),
    public=True,
    permission_classes=[permissions.IsAuthenticated],
)

swagger_urlpatterns = [
    # Documentação Swagger/OpenAPI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] 