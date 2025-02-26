import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack

# Set Django settings module before importing routing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voteitout.settings')
django_asgi_app = get_asgi_application()

# Import routing after Django setup
from api.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": SessionMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})