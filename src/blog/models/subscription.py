from django.db import models


class Subscription(models.Model):
    to_user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        verbose_name="user",
        related_name="subscribers"
    )

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        verbose_name="user",
        related_name="subscriptions"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

        unique_together = (
            (
                "to_user",
                "user"
            )
        )
