import os
from django.core.asgi import get_asgi_application
import socketio

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

sio = socketio.AsyncServer(async_mode="asgi")
django_asgi = get_asgi_application()          # sua app Django
application = socketio.ASGIApp(
    sio, django_asgi, socketio_path="ws/socket.io"
)
