
from django.urls import path, include

urlpatterns = [
    path('auth/', include('users.api.urls')),
    path('course/', include('courses.api.urls')),
    path('notifications/', include('notifications.routing')),
]