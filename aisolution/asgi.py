"""
ASGI config for genai project.
 
It exposes the ASGI callable as a module-level variable named ``application``.
 
For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""
 
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aisolution.settings")
get_application = get_asgi_application()
 
from qna.websockets_urls import websocket_urlpatterns
from auth.asyncMiddleware import AsyncAuthMiddleware

application = ProtocolTypeRouter(
    {
        "http": get_application,
        "websocket": AsyncAuthMiddleware(AuthMiddlewareStack(URLRouter(websocket_urlpatterns))),
    }
)