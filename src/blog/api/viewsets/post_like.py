from rest_framework import viewsets, serializers, permissions, exceptions, status
from rest_framework.response import Response

from blog.api.permissions import post as custom_permissions
from blog.models import Post, PostLike


class PostLikeViewSet(viewsets.GenericViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.PostNoOwner
    ]

    serializer_class = serializers.Serializer

    queryset = Post.objects

    def create(self, request, *args, **kwargs):
        post = self.get_object()
        if post.likes.filter(user_id=request.user.pk).exists():
            raise exceptions.PermissionDenied

        PostLike.objects.create(
            user_id=request.user.pk,
            post_id=post.pk
        )
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if not post.likes.filter(user_id=request.user.pk).exists():
            raise exceptions.NotFound

        PostLike.objects.filter(
            user_id=request.user.pk,
            post_id=post.pk
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
