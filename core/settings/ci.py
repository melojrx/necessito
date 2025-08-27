"""
Configurações específicas para CI/CD (GitHub Actions)
"""
from .dev import *
import os

# Configurações específicas para ambiente de testes CI
DEBUG = False  # Para testes mais próximos da produção

# Banco de dados para CI com serviços do GitHub Actions
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'test'),
        'USER': os.environ.get('DB_USER', 'test'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'test'),
        'HOST': os.environ.get('DB_HOST', 'postgres'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Redis/Cache para CI
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:6379/1',
        'KEY_PREFIX': 'ci_test',
        'TIMEOUT': 300,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 10},
            'PICKLE_VERSION': 2,
        },
    }
}

# Configurações para acelerar testes
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Mais rápido para testes
]

# Email backend para testes
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Desabilitar logging desnecessário durante testes
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Configurações de arquivo estático para CI
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files para testes
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Configurações específicas para testes
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Configurações reCAPTCHA para testes
RECAPTCHA_PUBLIC_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'  # Chave de teste do Google
RECAPTCHA_PRIVATE_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'  # Chave de teste do Google
RECAPTCHA_REQUIRED_SCORE = 0.85

# Silenciar warnings desnecessários em CI
SILENCED_SYSTEM_CHECKS = [
    'django_recaptcha.recaptcha_test_key_error',
    'security.W019',  # X-Frame-Options não é necessário em testes
    'security.W012',  # SESSION_COOKIE_SECURE não é necessário em testes
    'security.W004',  # SECURE_HSTS_SECONDS não é necessário em testes
    'security.W008',  # SECURE_SSL_REDIRECT não é necessário em testes
]

# Configurações de segurança simplificadas para CI
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False