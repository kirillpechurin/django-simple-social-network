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

    path('auth/forgot-password', viewsets.PasswordViewSet.as_view({
        "post": "forgot"
    })),

    path('auth/reset-password', viewsets.PasswordViewSet.as_view({
        "post": "reset"
    })),

    path('auth/confirm-email', viewsets.AuthViewSet.as_view({
        "post": "confirm_email"
    })),

    path('auth/resend-confirm-email', viewsets.AuthViewSet.as_view({
        "post": "resend_confirm_email"
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

    # Account
    path("account", viewsets.AccountViewSet.as_view({
        "get": "retrieve",
        "put": "update"
    })),

    path("account/password", viewsets.PasswordViewSet.as_view({
        "post": "update",
    }))

])
