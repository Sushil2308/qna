from django.urls import re_path
from qna.websocket_streaming import QnaStreamConsumer

websocket_urlpatterns = [
    re_path("docChat/", QnaStreamConsumer.as_asgi(), name="Doc Chat End Point"),
]
