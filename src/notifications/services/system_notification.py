from typing import List

from notifications.models import SystemNotification
from users.models import User


class SystemNotificationService:

    @staticmethod
    def read_by_ids(user: User,
                    ids: List[int]):
        SystemNotification.objects.filter(
            user_id=user.pk,
            id__in=ids
        ).update(
            is_read=True
        )

    @staticmethod
    def read_all(user: User):
        SystemNotification.objects.filter(
            user_id=user.pk,
        ).update(
            is_read=True
        )
