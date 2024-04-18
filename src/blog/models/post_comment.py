from django.db import models


class PostComment(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        verbose_name="user",
        related_name="post_comments"
    )

    post = models.ForeignKey(
        "blog.Post",
        on_delete=models.CASCADE,
        verbose_name="post",
        related_name="comments"
    )

    comment = models.TextField(
        verbose_name="comment"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Post comment"
        verbose_name_plural = "Post comments"
