from .base import *

DEBUG = False
ALLOWED_HOSTS = ["31.97.17.10", "www.necessito.br"]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SECURE_SSL_REDIRECT =  False
SESSION_COOKIE_SECURE =  False
CSRF_COOKIE_SECURE = False