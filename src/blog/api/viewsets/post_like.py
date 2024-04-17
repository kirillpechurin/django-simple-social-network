from rest_framework import viewsets, serializers, permissions, status
from rest_framework.response import Response

from blog.api.permissions import post as custom_permissions
from blog.models import Post
from blog.services.post_like import PostLikeService


class PostLikeViewSet(viewsets.GenericViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.PostNoOwner
    ]

    serializer_class = serializers.Serializer

    queryset = Post.objects

    def create(self, request, *args, **kwargs):
        post = self.get_object()
        PostLikeService.add_like(
            post,
            request.user
        )
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        PostLikeService.remove_like(
            post,
            request.user
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
