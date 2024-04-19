from django_filters import rest_framework as rest_filters
from rest_framework import viewsets, permissions, serializers, status
from rest_framework.response import Response

from blog.api.filters import subscription as custom_filters
from blog.api.serializers.subscription import (
    SubscriptionListSerializer,
    SubscriptionCreateSerializer,
    SubscriberListSerializer
)
from blog.models import Subscription
from blog.services import SubscriptionService
from common.api import pagination as custom_pagination


class SubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    pagination_class = custom_pagination.PageCountPagination

    serializer_class = serializers.Serializer

    queryset = Subscription.objects

    filterset_class = custom_filters.SubscriptionFilter
    filter_backends = [
        rest_filters.DjangoFilterBackend,
        custom_filters.SubscriptionOrderingFilter
    ]

    def get_serializer_class(self):
        if self.action == "list":
            return SubscriptionListSerializer
        elif self.action == "create":
            return SubscriptionCreateSerializer
        else:
            raise NotImplementedError

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        SubscriptionService.create(
            user=self.request.user,
            data=serializer.validated_data
        )
        return Response(status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        SubscriptionService.delete(
            user=self.request.user,
            subscription=instance
        )


class SubscriberViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    pagination_class = custom_pagination.PageCountPagination

    serializer_class = serializers.Serializer

    queryset = Subscription.objects

    filterset_class = custom_filters.SubscriberFilter
    filter_backends = [
        rest_filters.DjangoFilterBackend,
        custom_filters.SubscriberOrderingFilter
    ]

    def get_serializer_class(self):
        if self.action == "list":
            return SubscriberListSerializer
        else:
            raise NotImplementedError
