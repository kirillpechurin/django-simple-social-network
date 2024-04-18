from django_filters import rest_framework as rest_filters
from rest_framework import viewsets, serializers, permissions

from blog.api.filters import post as custom_filters
from blog.api.permissions import post as custom_permissions
from blog.api.serializers.post import (
    PostListSerializer,
    PostCreateSerializer,
    PostSerializer,
    PostUpdateSerializer
)
from blog.models import Post
from blog.services import PostService
from common.api import pagination as custom_pagination


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.PostOwnerOrReadOnly
    ]

    pagination_class = custom_pagination.PageCountPagination

    serializer_class = serializers.Serializer

    queryset = Post.objects

    filterset_class = custom_filters.PostFilter
    filter_backends = [
        rest_filters.DjangoFilterBackend,
        custom_filters.PostOrderingFilter
    ]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        elif self.action == "create":
            return PostCreateSerializer
        elif self.action == "retrieve":
            return PostSerializer
        elif self.action == "partial_update":
            return PostUpdateSerializer
        else:
            return self.serializer_class

    def perform_create(self, serializer):
        post = PostService.create(
            user=self.request.user,
            data=serializer.validated_data
        )
        serializer.instance = post
