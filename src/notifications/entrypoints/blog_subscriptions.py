from notifications.models import SystemNotification, SystemNotificationType, NotificationEvent


class BlogSubscriptionsEntrypoint:

    def accept(self, action: str, **kwargs):
        if action == "BLOG_SUBSCRIPTIONS_NEW":
            return self._blog_subscriptions_new(**kwargs)
        else:
            raise NotImplementedError

    def _blog_subscriptions_new(self,
                                data: dict):
        SystemNotification.objects.create(
            user_id=data["to_user"]["id"],
            type_id=SystemNotificationType.Handbook.BLOG_SUBSCRIPTIONS.value,
            event_id=NotificationEvent.Handbook.BLOG_SUBSCRIPTIONS_NEW.value,
            message=f'New subscriber.',
            payload={
                "from_user": {
                    "id": data["from_user"]["id"],
                    "username": data["from_user"]["username"]
                }
            },
        )
