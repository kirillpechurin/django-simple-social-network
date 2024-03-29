from rest_framework import viewsets, serializers, status, permissions
from rest_framework.response import Response

from users.api.serializers.password import (
    PasswordUpdateSerializer,
    PasswordForgotSerializer,
    PasswordResetSerializer
)
from users.services.auth import AuthService


class PasswordViewSet(viewsets.GenericViewSet):
    serializer_class = serializers.Serializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_permissions(self):
        if self.action == "update":
            self.permission_classes = [
                permissions.IsAuthenticated
            ]
        elif self.action == "forgot":
            self.permission_classes = [
                permissions.AllowAny
            ]
        elif self.action == "reset":
            self.permission_classes = [
                permissions.AllowAny
            ]
        return super().get_permissions()

    def get_serializer_class(self, *args, **kwargs):
        if self.action == "update":
            return PasswordUpdateSerializer
        elif self.action == "forgot":
            return PasswordForgotSerializer
        elif self.action == "reset":
            return PasswordResetSerializer
        else:
            return self.serializer_class

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    def forgot(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        AuthService.process_forgot_password(
            data=serializer.validated_data
        )

        return Response(status=status.HTTP_200_OK)

    def reset(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        AuthService.process_reset_password(
            data=serializer.validated_data
        )

        return Response(status=status.HTTP_200_OK)
