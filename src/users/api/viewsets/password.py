from rest_framework import viewsets, serializers, status, permissions
from rest_framework.response import Response

from users.api.serializers.password import PasswordUpdateSerializer


class PasswordViewSet(viewsets.GenericViewSet):
    serializer_class = serializers.Serializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_serializer_class(self, *args, **kwargs):
        if self.action == "update":
            return PasswordUpdateSerializer
        else:
            return self.serializer_class

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)
