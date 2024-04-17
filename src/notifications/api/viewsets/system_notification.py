from django_filters import rest_framework as rest_filters
from rest_framework import viewsets, mixins, status, permissions
from rest_framework.response import Response

from common.api import pagination as custom_pagination
from notifications.api.filters import system_notification as custom_filters
from notifications.api.serializers.system_notification import (
    SystemNotificationSerializer,
    SystemNotificationReadSerializer
)
from notifications.models import SystemNotification
from notifications.services import SystemNotificationService


class SystemNotificationViewSet(mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    pagination_class = custom_pagination.PageCountPagination

    serializer_class = SystemNotificationSerializer

    queryset = SystemNotification.objects

    filterset_class = custom_filters.SystemNotificationFilter
    filter_backends = [
        rest_filters.DjangoFilterBackend,
        custom_filters.SystemNotificationOrderingFilter
    ]

    def get_serializer_class(self):
        if self.action == "list":
            return SystemNotificationSerializer
        elif self.action == "read":
            return SystemNotificationReadSerializer
        else:
            raise NotImplementedError

    def read(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        SystemNotificationService.read_by_ids(
            user=request.user,
            ids=serializer.validated_data["ids"]
        )
        return Response(status=status.HTTP_202_ACCEPTED)

    def read_all(self, request, *args, **kwargs):
        SystemNotificationService.read_all(
            user=request.user,
        )
        return Response(status=status.HTTP_202_ACCEPTED)
