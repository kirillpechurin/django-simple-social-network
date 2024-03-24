from django.urls import path
from rest_framework import routers

from . import viewsets

router = routers.DefaultRouter()

urlpatterns = router.urls

urlpatterns.extend([

    # Auth
    path('auth/registration', viewsets.AuthViewSet.as_view({
        "post": "registration"
    })),

    path('auth/login', viewsets.AuthViewSet.as_view({
        "post": "login"
    })),

    path('auth/refresh', viewsets.AuthViewSet.as_view({
        "post": "refresh"
    })),

    path('auth/logout', viewsets.AuthViewSet.as_view({
        "post": "logout"
    })),

])
