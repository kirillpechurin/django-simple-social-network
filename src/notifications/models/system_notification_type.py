from django.db import models


class SystemNotificationType(models.Model):
    class Handbook(models.IntegerChoices):
        BLOG_POSTS_LIKE = 1, "Like posts"

    title = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.title
