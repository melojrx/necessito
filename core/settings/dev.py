from .base import *

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "web"]

# Silenciar warning do reCAPTCHA para chaves de teste em desenvolvimento
SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']

# Configuração de logging para debug
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
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'chat.views': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'budgets.views': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

