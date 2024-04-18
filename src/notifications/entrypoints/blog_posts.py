from notifications.models import SystemNotification, SystemNotificationType, NotificationEvent


class BlogPostsEntrypoint:

    def accept(self, action: str, **kwargs):
        if action == "BLOG_POSTS_LIKE":
            return self._blog_posts_like(**kwargs)
        elif action == "BLOG_POSTS_LIKE_REMOVE":
            return self._blog_posts_like_remove(**kwargs)
        elif action == "BLOG_POSTS_NEW_COMMENT":
            return self._blog_posts_new_comment(**kwargs)
        else:
            raise NotImplementedError

    def _blog_posts_like(self,
                         data: dict):
        SystemNotification.objects.create(
            user_id=data["post"]["user_id"],
            type_id=SystemNotificationType.Handbook.BLOG_POSTS_LIKE.value,
            event_id=NotificationEvent.Handbook.BLOG_POSTS_LIKE.value,
            message=f'New like on your post.',
            payload={
                "post_id": data["post"]["id"],
                "from_user_id": data["from_user"]["id"],
            },
        )

    def _blog_posts_like_remove(self,
                                data: dict):
        SystemNotification.objects.filter(
            user_id=data["post"]["user_id"],
            event_id=NotificationEvent.Handbook.BLOG_POSTS_LIKE.value,
            payload__post_id=data["post"]["id"],
            is_read=False
        ).delete()

    def _blog_posts_new_comment(self,
                                data: dict):
        SystemNotification.objects.create(
            user_id=data["post"]["user_id"],
            type_id=SystemNotificationType.Handbook.BLOG_POSTS_COMMENTS.value,
            event_id=NotificationEvent.Handbook.BLOG_POSTS_NEW_COMMENT.value,
            message=f'New comment on your post.',
            payload={
                "post_id": data["post"]["id"],
                "from_user_id": data["from_user"]["id"],
            },
        )
