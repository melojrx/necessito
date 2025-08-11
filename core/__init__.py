# Isso garantirá que a aplicação seja sempre importada quando
# o Django iniciar para que shared_task use esta aplicação.
from .celery import app as celery_app

__all__ = ('celery_app',)