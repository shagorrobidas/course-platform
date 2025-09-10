from django.urls import re_path
from . import consumers

# WebSocket URL patterns
websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]

# Regular HTTP URL patterns (empty if you don't have HTTP endpoints in notifications)
urlpatterns = [
    # Add any HTTP endpoints here if needed
]