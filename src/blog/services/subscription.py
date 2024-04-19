from rest_framework import exceptions

from blog.models import Subscription
from notifications import Handler as NotificationsHandler
from users.models import User


class SubscriptionService:

    @staticmethod
    def create(user: User,
               data: dict) -> Subscription:
        if data["to_user_id"] == user.pk:
            raise exceptions.PermissionDenied

        to_user = User.objects.filter(id=data["to_user_id"]).first()
        if not to_user:
            raise exceptions.PermissionDenied

        if Subscription.objects.filter(to_user_id=to_user.pk, user_id=user.pk).exists():
            raise exceptions.PermissionDenied(detail="You have already subscribed.")

        subscription = Subscription.objects.create(
            to_user_id=to_user.pk,
            user_id=user.pk
        )

        NotificationsHandler.accept(
            action="BLOG_SUBSCRIPTIONS_NEW",
            data={
                "to_user": {
                    "id": to_user.pk,
                },
                "from_user": {
                    "id": user.pk,
                    "username": user.username
                }
            }
        )

        return subscription

    @staticmethod
    def delete(user: User,
               subscription: Subscription) -> None:
        if subscription.user_id != user.pk:
            raise exceptions.PermissionDenied

        subscription.delete()
