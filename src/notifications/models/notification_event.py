from django.db import models


class NotificationEvent(models.Model):
    class Handbook(models.IntegerChoices):
        BLOG_POSTS_LIKE = 1, "Like post"
        BLOG_POSTS_NEW_COMMENT = 2, "Comment post"
        BLOG_SUBSCRIPTIONS_NEW = 3, "New subscriber"
        BLOG_POSTS_NEW = 4, "New post"

    title = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.title
