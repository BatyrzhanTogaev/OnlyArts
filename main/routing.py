from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/artwork/<int:artwork_id>/', consumers.ArtworkConsumer.as_asgi()),
]
