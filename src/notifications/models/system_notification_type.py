from django.db import models


class SystemNotificationType(models.Model):
    class Handbook(models.IntegerChoices):
        BLOG_POSTS_LIKE = 1, "Like posts"
        BLOG_POSTS_COMMENTS = 2, "Comment posts"

    title = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.title
