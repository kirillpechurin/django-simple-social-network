from django.db import models


class PostLike(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        verbose_name="user",
        related_name="post_likes"
    )

    post = models.ForeignKey(
        "blog.Post",
        on_delete=models.CASCADE,
        verbose_name="post",
        related_name="likes"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Post like"
        verbose_name_plural = "Post likes"

        unique_together = (
            (
                "user",
                "post"
            )
        )
