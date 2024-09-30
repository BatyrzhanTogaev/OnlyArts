from django.urls import re_path
from .consumers import ArtworkConsumer

websocket_urlpatterns = [
    re_path(r'ws/artwork/(?P<artwork_id>\d+)/$', ArtworkConsumer.as_asgi()),
]
