from typing import Type

from rest_framework import serializers, viewsets
from rest_framework_simplejwt import serializers as simple_jwt_serializers
from rest_framework_simplejwt import views as simple_jwt_viewsets


class AuthViewSet(viewsets.ViewSetMixin, simple_jwt_viewsets.TokenViewBase):
    serializer_class = serializers.Serializer
    permission_classes = []
    authentication_classes = []

    def get_serializer_class(self) -> Type[serializers.Serializer]:
        if self.action == "login":
            return simple_jwt_serializers.TokenObtainPairSerializer
        elif self.action == "refresh":
            return simple_jwt_serializers.TokenRefreshSerializer
        elif self.action == "refresh":
            return simple_jwt_serializers.TokenBlacklistSerializer
        else:
            return self.serializer_class

    def login(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def refresh(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def logout(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
