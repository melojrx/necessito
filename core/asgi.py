import os
from django.core.asgi import get_asgi_application
import socketio

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Criar servidor Socket.IO
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

# Importar e registrar namespaces após criação do Django
django_asgi = get_asgi_application()

# Importar namespace do chat
from chat.consumers import ChatNamespace
sio.register_namespace(ChatNamespace('/chat'))

# Configurar aplicação ASGI
application = socketio.ASGIApp(
    sio, django_asgi, socketio_path="ws/socket.io"
)
