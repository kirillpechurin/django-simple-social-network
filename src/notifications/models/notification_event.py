from django.db import models


class NotificationEvent(models.Model):
    class Handbook(models.IntegerChoices):
        BLOG_POSTS_LIKE = 1, "Like post"
        BLOG_POSTS_NEW_COMMENT = 2, "Comment post"

    title = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.title
