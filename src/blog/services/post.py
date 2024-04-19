from blog.models import Post
from notifications import Handler as NotificationsHandler
from users.models import User


class PostService:

    @staticmethod
    def create(user: User,
               data: dict) -> Post:
        post = Post.objects.create(
            user_id=user.pk,
            content=data["content"]
        )

        subscriber_user_ids = list(user.subscribers.order_by("user_id").values_list("user_id", flat=True))
        if len(subscriber_user_ids):
            NotificationsHandler.accept(
                action="BLOG_POSTS_NEW",
                data={
                    "post": {
                        "id": post.pk,
                        "user": {
                            "id": user.pk,
                            "username": user.username
                        }
                    },
                    "to_user_ids": subscriber_user_ids
                }
            )

        return post
