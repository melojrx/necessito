from .base import *

DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

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
    },
}

