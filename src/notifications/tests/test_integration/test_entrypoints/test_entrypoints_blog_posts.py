from django.core import mail
from django.test import TestCase

from notifications.entrypoints import BlogPostsEntrypoint
from notifications.models import SystemNotification, SystemNotificationType, NotificationEvent
from users.models import User


class NotificationsBlogPostsEntrypointIntegrationTestCase(TestCase):
    fixtures = [
        "notifications/fixtures/notificationevent.json",
        "notifications/fixtures/systemnotificationtype.json",
    ]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.post_user = User.objects.create_user(username="test-1")

    def _call(self,
              action: str,
              **kwargs):
        BlogPostsEntrypoint().accept(action, **kwargs)

    def test_blog_posts_like(self):
        self._call(
            action="BLOG_POSTS_LIKE",
            data={
                "post": {
                    "id": 1,
                    "user_id": self.post_user.pk,
                },
                "from_user": {
                    "id": 2
                }
            }
        )

        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(SystemNotification.objects.count(), 1)

        notification: SystemNotification = SystemNotification.objects.get()
        self.assertEqual(notification.user_id, self.post_user.pk)
        self.assertEqual(notification.type_id, SystemNotificationType.Handbook.BLOG_POSTS_LIKE.value)
        self.assertEqual(notification.event_id, NotificationEvent.Handbook.BLOG_POSTS_LIKE.value)
        self.assertEqual(notification.message, "New like on your post.")
        self.assertEqual(notification.payload, {
            "post_id": 1,
            "from_user_id": 2,
        })

    def test_blog_posts_like_remove(self):
        self.test_blog_posts_like()

        self._call(
            action="BLOG_POSTS_LIKE_REMOVE",
            data={
                "post": {
                    "id": 1,
                    "user_id": self.post_user.pk,
                },
                "from_user": {
                    "id": 2
                }
            }
        )

        self.assertEqual(SystemNotification.objects.count(), 0)

    def test_blog_posts_like_remove_other_user(self):
        self.test_blog_posts_like()

        other_user = User.objects.create(username="test-2")

        self._call(
            action="BLOG_POSTS_LIKE_REMOVE",
            data={
                "post": {
                    "id": 1,
                    "user_id": other_user.pk,
                },
                "from_user": {
                    "id": 2
                }
            }
        )
        self.assertEqual(SystemNotification.objects.count(), 1)

    def test_blog_posts_like_remove_other_event(self):
        self.test_blog_posts_like()

        event = NotificationEvent.objects.create(title="other")
        notification: SystemNotification = SystemNotification.objects.get()
        notification.event_id = event.pk
        notification.save(update_fields=["event_id"])

        self._call(
            action="BLOG_POSTS_LIKE_REMOVE",
            data={
                "post": {
                    "id": 1,
                    "user_id": self.post_user.pk,
                },
                "from_user": {
                    "id": 2
                }
            }
        )
        self.assertEqual(SystemNotification.objects.count(), 1)

    def test_blog_posts_like_remove_other_post_id(self):
        self.test_blog_posts_like()

        self._call(
            action="BLOG_POSTS_LIKE_REMOVE",
            data={
                "post": {
                    "id": 4,
                    "user_id": self.post_user.pk,
                },
                "from_user": {
                    "id": 2
                }
            }
        )
        self.assertEqual(SystemNotification.objects.count(), 1)

    def test_blog_posts_like_remove_already_read(self):
        self.test_blog_posts_like()

        notification: SystemNotification = SystemNotification.objects.get()
        notification.is_read = True
        notification.save(update_fields=["is_read"])

        self._call(
            action="BLOG_POSTS_LIKE_REMOVE",
            data={
                "post": {
                    "id": 4,
                    "user_id": self.post_user.pk,
                },
                "from_user": {
                    "id": 2
                }
            }
        )
        self.assertEqual(SystemNotification.objects.count(), 1)

    def test_unknown_action(self):
        self.assertRaises(NotImplementedError, self._call, action="UNKNOWN_ACTION", data={})
