from django.db import models


class Post(models.Model):

    user = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        verbose_name="user",
        related_name="posts"
    )

    content = models.CharField(
        max_length=500
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
