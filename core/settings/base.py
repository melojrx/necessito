from pathlib import Path
from django.contrib.messages import constants as messages
import os
from dotenv import load_dotenv

# Diretórios base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_DIR = os.path.join(BASE_DIR,'templates')
STATIC_DIR=os.path.join(BASE_DIR,'static')

# Tag para o Django encontrar o arquivo .env
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Segurança e chaves
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-temporary-key-for-development")

# reCAPTCHA
RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")

# Modo Debug
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

# Hosts permitidos
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Usuário customizado
AUTH_USER_MODEL = 'users.User'

# Sites
SITE_ID = 1

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

# Banco de dados
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

# Validadores de senha
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

# Localização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Arquivos estáticos e mídia
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # pasta para desenvolvimento
]
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'ads:home'
LOGOUT_REDIRECT_URL = '/'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Personalização dos níveis de mensagens
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# Configurações de e-mail via variáveis de ambiente
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Indicai <no-reply@indicai.com.br>")
EMAIL_SUBJECT_PREFIX = os.environ.get("EMAIL_SUBJECT_PREFIX", "[Indicai]")

# Uploads
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

# Segurança
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Alterado de DENY para SAMEORIGIN para permitir reCAPTCHA

if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# DRF
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

# SPECTACULAR
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

    1. **Faça login** no endpoint `/api/v1/auth/login/` com email e senha
    2. **Copie o access token** da resposta
    3. **Clique em "Authorize"** no topo da página
    4. **Cole o token** no campo "Value" (apenas o token, sem "Bearer")
    5. **Clique em "Authorize"** novamente
    6. **Use os endpoints** normalmente por 1 hora (duração do token)

    A API utiliza versionamento via URL. A versão atual é **v1**.

    A API utiliza autenticação JWT. O token de acesso tem duração de 1 hora.
    ''',
}

# Allauth
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'optional' # ou 'mandatory' ou 'none'

SITE_ID = 1 # dj-rest-auth requer isso

# CORS
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

# Celery Beat Schedule
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'handle-confirmation-timeouts': {
        'task': 'ads.tasks.handle_confirmation_timeouts',
        'schedule': crontab(minute=0),  # Every hour
    },
    'send-timeout-notifications': {
        'task': 'ads.tasks.send_timeout_notifications',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    'cleanup-expired-necessidades': {
        'task': 'ads.tasks.cleanup_expired_necessidades',
        'schedule': crontab(minute=0, hour=2),  # Daily at 2 AM
    },
}
