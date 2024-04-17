from django.db import models


class SystemNotification(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        verbose_name="user",
        related_name="system_notifications"
    )

    type = models.ForeignKey(
        "notifications.SystemNotificationType",
        on_delete=models.PROTECT,
        verbose_name="type",
        related_name="notifications"
    )

    event = models.ForeignKey(
        "notifications.NotificationEvent",
        on_delete=models.PROTECT,
        verbose_name="event",
        related_name="system_notifications"
    )

    message = models.TextField(
        verbose_name="message",
    )

    is_read = models.BooleanField(
        verbose_name="read status",
        default=False
    )

    payload = models.JSONField(
        verbose_name="payload",
        default=dict
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )
