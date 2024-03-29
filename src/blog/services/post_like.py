from rest_framework import exceptions

from blog.models import Post, PostLike
from users.models import User
from notifications import Handler as NotificationsHandler


class PostLikeService:

    @staticmethod
    def add_like(post: Post,
                 user: User):
        if post.likes.filter(user_id=user.pk).exists():
            raise exceptions.PermissionDenied

        PostLike.objects.create(
            user_id=user.pk,
            post_id=post.pk
        )

        NotificationsHandler.accept(
            action="BLOG_POSTS_LIKE",
            data={
                "post_id": post.pk,
                "user_id": user.pk
            }
        )

    @staticmethod
    def remove_like(post: Post,
                    user: User):
        if not post.likes.filter(user_id=user.pk).exists():
            raise exceptions.NotFound

        PostLike.objects.filter(
            user_id=user.pk,
            post_id=post.pk
        ).delete()

        NotificationsHandler.accept(
            action="BLOG_POSTS_LIKE_REMOVE",
            data={
                "post_id": post.pk,
                "user_id": user.pk
            }
        )
