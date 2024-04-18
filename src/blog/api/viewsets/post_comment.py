from rest_framework import viewsets, permissions, exceptions

from blog.api.filters import post_comment as custom_filters
from blog.api.permissions import post_comment as custom_permissions
from blog.api.serializers.post_comment import PostCommentListSerializer, PostCommentCreateSerializer, \
    PostCommentUpdateSerializer
from blog.models import Post, PostComment
from blog.services import PostCommentService
from common.api import pagination as custom_pagination


class PostCommentViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.PostNoOwnerOrReadOnly,
        custom_permissions.PostCommentOwnerOrReadOnly,
    ]

    pagination_class = custom_pagination.PageCountPagination

    queryset = PostComment.objects

    filter_backends = [
        custom_filters.PostCommentOrderingFilter
    ]

    def get_post(self):
        post = Post.objects.filter(id=self.kwargs.get("post_id")).first()
        if not post:
            raise exceptions.NotFound
        return post

    def get_queryset(self):
        post = self.get_post()
        return post.comments.all()

    def get_serializer_class(self):
        if self.action == "list":
            return PostCommentListSerializer
        elif self.action == "create":
            return PostCommentCreateSerializer
        elif self.action == "update":
            return PostCommentUpdateSerializer
        else:
            raise NotImplementedError

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["post_id"] = self.get_post().pk
        return context

    def perform_create(self, serializer):
        post_comment = PostCommentService.create(
            post=self.get_post(),
            user=self.request.user,
            data=serializer.validated_data
        )
        serializer.instance = post_comment

    def perform_update(self, serializer):
        post_comment = PostCommentService.update(
            post_comment=serializer.instance,
            data=serializer.validated_data
        )
        serializer.instance = post_comment
