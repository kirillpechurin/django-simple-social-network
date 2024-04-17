from django.test import tag
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from notifications.models import SystemNotification, SystemNotificationType, NotificationEvent
from users.models import User


class _BaseTestCase(APITestCase):
    fixtures = [
        "notifications/fixtures/notificationevent.json",
        "notifications/fixtures/systemnotificationtype.json",
    ]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user_1 = User.objects.create_user(email="test-1@gmail.com", username="test-1")
        cls.user_2 = User.objects.create_user(email="test-2@gmail.com", username="test-2")
        cls.user_3 = User.objects.create_user(email="test-3@gmail.com", username="test-3")
        for user in [cls.user_1, cls.user_2, cls.user_3]:
            for i in range(0, 5):
                SystemNotification.objects.create(
                    user_id=user.pk,
                    type_id=SystemNotificationType.Handbook.BLOG_POSTS_LIKE.value,
                    event_id=NotificationEvent.Handbook.BLOG_POSTS_LIKE.value,
                    message=f'New like on your post.',
                    payload={
                        "post_id": 11,
                        "from_user_id": 12,
                    },
                )

    def setUp(self) -> None:
        super().setUp()

        self.client.force_authenticate(user=self.user_1, token=str(RefreshToken.for_user(self.user_1).access_token))

        self.url = "/api/v1/notifications"


@tag("api-tests", "notifications")
class SystemNotificationListAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_response_data(self):
        resp = self.client.get(self.url)
        self.assertIsInstance(resp.data, dict)
        data: dict = resp.data
        self.assertEqual(data["count"], SystemNotification.objects.count())
        self.assertEqual(data["next"], 2)
        self.assertEqual(data["previous"], None)
        self.assertEqual(len(data["results"]), 10)

        for item, notification in zip(resp.data["results"], SystemNotification.objects.order_by("-created_at")):
            self.assertEqual(item.pop("id"), notification.id)
            self.assertEqual(item.pop("type_id"), notification.type_id)
            self.assertEqual(item.pop("event_id"), notification.event_id)
            self.assertEqual(item.pop("message"), notification.message)
            self.assertEqual(item.pop("is_read"), notification.is_read)
            self.assertEqual(item.pop("payload"), notification.payload)
            self.assertIsNotNone(item.pop("created_at"))
            self.assertIsNotNone(item.pop("updated_at"))

            self.assertEqual(item, {})

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")


@tag("api-tests", "notifications")
class PostListFilterAPITestCase(_BaseTestCase):

    def test_by_type_id(self):
        resp = self.client.get(self.url, data={"type_id": SystemNotificationType.Handbook.BLOG_POSTS_LIKE.value})
        self.assertEqual(resp.data["count"], SystemNotification.objects.count())

        system_notification_type = SystemNotificationType.objects.create(title="test-1")
        resp = self.client.get(self.url, data={"type_id": system_notification_type.pk})
        self.assertEqual(resp.data["count"], 0)


@tag("api-tests", "notifications")
class SystemNotificationListOrderingFilterAPITestCase(_BaseTestCase):

    def test_by_created_at_asc(self):
        resp = self.client.get(self.url, data={"ordering": "created_at"})

        for item, notification in zip(resp.data["results"], SystemNotification.objects.order_by("created_at")):
            self.assertEqual(item["id"], notification.pk)

    def test_by_created_at_desc(self):
        resp = self.client.get(self.url, data={"ordering": "-created_at"})

        for item, notification in zip(resp.data["results"], SystemNotification.objects.order_by("-created_at")):
            self.assertEqual(item["id"], notification.pk)
