from django.urls import path
from rest_framework import routers

from . import viewsets

router = routers.DefaultRouter()

urlpatterns = router.urls

urlpatterns.extend([

    # Posts
    path("notifications", viewsets.SystemNotificationViewSet.as_view({
        "get": "list",
    })),

    path("notifications/read", viewsets.SystemNotificationViewSet.as_view({
        "post": "read",
    })),

    path("notifications/read-all", viewsets.SystemNotificationViewSet.as_view({
        "post": "read_all",
    })),

])
