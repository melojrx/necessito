from django.urls import path, include

# URLs de autenticação usando as views padrão do dj-rest-auth
# As tags serão aplicadas via configuração do Swagger

auth_urlpatterns = [
    # Usar as URLs padrão do dj-rest-auth
    path('', include('dj_rest_auth.urls')),
]

registration_urlpatterns = [
    # Usar as URLs padrão do dj-rest-auth registration
    path('', include('dj_rest_auth.registration.urls')),
] 