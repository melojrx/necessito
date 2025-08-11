from pathlib import Path
from django.contrib.messages import constants as messages
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_DIR = os.path.join(BASE_DIR,'templates')
STATIC_DIR=os.path.join(BASE_DIR,'static')

# Tag para o Django encontrar o arquivo .env
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-temporary-key-for-development")

RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# Configurações CSRF para resolver problemas com origens confiáveis
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

AUTH_USER_MODEL = 'users.User'

# ID do site (necessário para django.contrib.sites)
SITE_ID = 1

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # Necessário para envio de e-mails
    "django_recaptcha",
    "corsheaders",  # CORS headers
    "core",
    "users",
    "ads",
    "categories",
    "budgets",
    "rankings",
    "notifications",
    "search",
    "chat",
    "admin_panel",
    
    # API e documentação
    "rest_framework",
    "rest_framework.authtoken", # Necessário para dj-rest-auth
    "dj_rest_auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "dj_rest_auth.registration",
    "drf_spectacular",
    "django_filters",
    "django_celery_beat",
    "django_celery_results",
    "api",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # CORS deve ser o primeiro
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware", # Adicionado para allauth
    "api.middleware.APIVersionMiddleware",  # Middleware de versionamento da API
    "core.middleware.ProfileCompleteMiddleware",  # Reativado com melhorias
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "core.context_processors.unread_notifications",
                "core.context_processors.unread_messages",
            ],
        },
    },
]

TEMPLATES[0]["OPTIONS"]["context_processors"] += [
    "search.context_processors.states_list",
]

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get('DB_NAME'),
        "USER": os.environ.get('DB_USER'),
        "PASSWORD": os.environ.get('DB_PASSWORD'),
        "HOST": os.environ.get('DB_HOST'),
        "PORT": os.environ.get('DB_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# Settings.py

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # pasta para desenvolvimento
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/home'
LOGOUT_REDIRECT_URL = '/'

# Configurações relacionadas a proxies e balanceadores de carga
# USE_X_FORWARDED_HOST = True  # Comentado temporariamente para debug

# Indica que o Django deve respeitar o cabeçalho X-Forwarded-Proto
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Opcional: Personalizar os níveis de mensagens
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# Se quiser ver os e-mails diretamente no console (modo dev):
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = "Indicai <no-reply@indicai.com.br>"
EMAIL_SUBJECT_PREFIX = "[Indicai]"

# Backend de e-mail
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Indicai <no-reply@indicai.com.br>")
EMAIL_SUBJECT_PREFIX = os.environ.get("EMAIL_SUBJECT_PREFIX", "[Indicai]")

# Tamanho máximo de upload (10MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

# Configurações de segurança
# Em desenvolvimento (DEBUG=True), permitir HTTP
# Em produção (DEBUG=False), forçar HTTPS
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Alterado de DENY para SAMEORIGIN para permitir reCAPTCHA

# HSTS apenas em produção
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Configurações REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'URL_FIELD_NAME': 'url',
}

# Configurações removidas - usando apenas drf_spectacular

# Configurações DRF Spectacular
SPECTACULAR_SETTINGS = {
    'TITLE': 'API Indicai',
    'DESCRIPTION': '''
    API de integração do sistema Indicai.
    
    Esta API fornece acesso às principais funcionalidades do sistema, incluindo:
    - Autenticação JWT (dj-rest-auth)
    - Gerenciamento de usuários
    - Categorias e subcategorias
    - Necessidades (anúncios)
    - Orçamentos
    - Avaliações
    
    ## Como usar a API
    
    1. **Faça login** no endpoint `/api/v1/auth/login/` com email e senha
    2. **Copie o access token** da resposta
    3. **Clique em "Authorize"** no topo da página
    4. **Cole o token** no campo "Value" (apenas o token, sem "Bearer")
    5. **Clique em "Authorize"** novamente
    6. **Use os endpoints** normalmente por 1 hora (duração do token)
    
    ## Versionamento
    
    A API utiliza versionamento via URL. A versão atual é **v1**.
    
    ## Autenticação
    
    A API utiliza autenticação JWT. O token de acesso tem duração de 1 hora.
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    'COMPONENTS': {
        'securitySchemes': {
            'bearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
                'description': 'Token JWT obtido através do endpoint de login'
            }
        }
    },
    'SECURITY': [{'bearerAuth': []}],
    'TAGS': [
        {'name': '00 - SISTEMA - INFORMAÇÕES GERAIS', 'description': 'Informações sobre versões e sistema'},
        {'name': '01 - USUÁRIOS - GESTÃO DE PERFIS', 'description': 'Gerenciamento de usuários do sistema'},
        {'name': '02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS', 'description': 'Categorias de produtos e serviços'},
        {'name': '03 - SUBCATEGORIAS - ESPECIALIZAÇÃO DE SERVIÇOS', 'description': 'Subcategorias especializadas'},
        {'name': '04 - NECESSIDADES - ANÚNCIOS DE DEMANDA', 'description': 'Anúncios de necessidades dos clientes'},
        {'name': '05 - ORÇAMENTOS - PROPOSTAS DE FORNECEDORES', 'description': 'Propostas de fornecedores'},
        {'name': '06 - AVALIAÇÕES - SISTEMA DE REPUTAÇÃO', 'description': 'Sistema de avaliações entre usuários'},
        {'name': '07 - AUTENTICAÇÃO - ACESSO AO SISTEMA', 'description': 'Endpoints de autenticação e acesso'},
    ],
    'CONTACT': {
        'email': 'contato@indicai.com.br',
    },
    'LICENSE': {
        'name': 'Licença Proprietária',
    },
    'TERMS_OF_SERVICE': 'https://indicai.com.br/termos/',
}

# Configurações removidas - usando apenas drf_spectacular

# Configurações de logging
# Criar diretório de logs se não existir
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_DIR, 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Configurações SimpleJWT
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),  # Token de acesso válido por 1 hora
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # Token de refresh válido por 7 dias
    'ROTATE_REFRESH_TOKENS': True,  # Gera novo refresh token a cada uso
    'BLACKLIST_AFTER_ROTATION': True,  # Invalida o refresh token anterior
    'UPDATE_LAST_LOGIN': True,  # Atualiza last_login do usuário
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': 'Indicai',
    'JSON_ENCODER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(hours=1),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}

# Configurações DJ-REST-AUTH
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'jwt-auth-token',
    'JWT_AUTH_REFRESH_COOKIE': 'jwt-refresh-token',
    'USER_DETAILS_SERIALIZER': 'api.serializers.UserDetailSerializer',
    'LOGIN_SERIALIZER': 'api.serializers.CustomLoginSerializer',
    'LOGOUT_ON_PASSWORD_CHANGE': False,
    'OLD_PASSWORD_FIELD_ENABLED': True,
    'LOGOUT_URL': '/api/v1/auth/logout/',
    'LOGIN_URL': '/api/v1/auth/login/',
    'SESSION_LOGIN': False,  # Desabilitar login de sessão
}

# Configurações Allauth
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'optional' # ou 'mandatory' ou 'none'


SITE_ID = 1 # dj-rest-auth requer isso
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # Para testes de email

# Configurações CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost",
    "http://127.0.0.1",
]

CORS_ALLOW_CREDENTIALS = True

# Em desenvolvimento, permitir todas as origens
CORS_ALLOW_ALL_ORIGINS = DEBUG

CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Configurações CSRF para API
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SAMESITE = 'Lax'

# Para desenvolvimento, permitir CSRF em localhost
if DEBUG:
    CSRF_TRUSTED_ORIGINS += [
        "http://localhost",
        "http://127.0.0.1",
    ]
    # Configurações mais permissivas para desenvolvimento
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r"^http://localhost:\d+$",
        r"^http://127\.0\.0\.1:\d+$",
    ]

# Configurações do Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/2')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/3')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ALWAYS_EAGER = os.environ.get('CELERY_TASK_ALWAYS_EAGER', 'False') == 'True'
CELERY_TASK_EAGER_PROPAGATES = os.environ.get('CELERY_TASK_EAGER_PROPAGATES', 'True') == 'True'
CELERY_WORKER_CONCURRENCY = int(os.environ.get('CELERY_WORKER_CONCURRENCY', '2'))
CELERY_BEAT_SCHEDULER = os.environ.get('CELERY_BEAT_SCHEDULER', 'django_celery_beat.schedulers:DatabaseScheduler')
