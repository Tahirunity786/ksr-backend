import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from processor.middleware import JwtAuthForAsgiStack
from core_messaging.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'processor.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JwtAuthForAsgiStack(
        URLRouter(websocket_urlpatterns)
    ),
})
