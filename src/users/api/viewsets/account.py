from rest_framework import viewsets, serializers, permissions

from users.api.serializers.account import AccountSerializer, AccountUpdateSerializer


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.Serializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AccountSerializer
        elif self.action == "update":
            return AccountUpdateSerializer
        else:
            return self.serializer_class

    def get_object(self):
        return self.request.user
