from django.core import mail
from django.test import TestCase

from notifications.entrypoints import BlogPostsEntrypoint, BlogSubscriptionsEntrypoint
from notifications.models import SystemNotification, SystemNotificationType, NotificationEvent
from users.models import User


class NotificationsBlogSubscriptionsEntrypointIntegrationTestCase(TestCase):
    fixtures = [
        "notifications/fixtures/notificationevent.json",
        "notifications/fixtures/systemnotificationtype.json",
    ]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.to_user = User.objects.create_user(email="test-1@gmail.com", username="test-1")
        cls.from_user = User.objects.create_user(email="test-2@gmail.com", username="test-2")

    def _call(self,
              action: str,
              **kwargs):
        BlogSubscriptionsEntrypoint().accept(action, **kwargs)

    def test_blog_subscriptions_new(self):
        self._call(
            action="BLOG_SUBSCRIPTIONS_NEW",
            data={
                "to_user": {
                    "id": self.to_user.pk,
                },
                "from_user": {
                    "id": self.from_user.pk,
                    "username": "sample"
                }
            }
        )

        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(SystemNotification.objects.count(), 1)

        notification: SystemNotification = SystemNotification.objects.get()
        self.assertEqual(notification.user_id, self.to_user.pk)
        self.assertEqual(notification.type_id, SystemNotificationType.Handbook.BLOG_SUBSCRIPTIONS.value)
        self.assertEqual(notification.event_id, NotificationEvent.Handbook.BLOG_SUBSCRIPTIONS_NEW.value)
        self.assertEqual(notification.message, "New subscriber.")
        self.assertEqual(notification.payload, {
            "from_user": {
                "id": self.from_user.pk,
                "username": "sample"
            },
        })

    def test_blog_subscriptions_new_from_user_check(self):
        self._call(
            action="BLOG_SUBSCRIPTIONS_NEW",
            data={
                "to_user": {
                    "id": self.to_user.pk,
                },
                "from_user": {
                    "id": 123,
                    "username": "sample"
                }
            }
        )

        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(SystemNotification.objects.count(), 1)

        notification: SystemNotification = SystemNotification.objects.get()
        self.assertEqual(notification.user_id, self.to_user.pk)
        self.assertEqual(notification.type_id, SystemNotificationType.Handbook.BLOG_SUBSCRIPTIONS.value)
        self.assertEqual(notification.event_id, NotificationEvent.Handbook.BLOG_SUBSCRIPTIONS_NEW.value)
        self.assertEqual(notification.message, "New subscriber.")
        self.assertEqual(notification.payload, {
            "from_user": {
                "id": 123,
                "username": "sample"
            },
        })

    def test_unknown_action(self):
        self.assertRaises(NotImplementedError, self._call, action="UNKNOWN_ACTION", data={})
