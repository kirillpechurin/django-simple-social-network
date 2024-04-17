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

        cls.user_1 = User.objects.create_user(username="test-1")
        cls.user_2 = User.objects.create_user(username="test-2")
        cls.user_3 = User.objects.create_user(username="test-3")
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

        self.url = "/api/v1/notifications/read-all"


@tag("api-tests", "notifications")
class SystemNotificationReadAllAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 202)

    def test_response_data(self):
        resp = self.client.post(self.url)
        self.assertEqual(resp.data, None)

    def test_entities(self):
        self.assertEqual(SystemNotification.objects.count(), 15)

        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 202)

        self.assertEqual(SystemNotification.objects.count(), 15)
        self.assertEqual(SystemNotification.objects.filter(is_read=True).count(), 5)

    def test_only_current_user(self):
        self.assertEqual(SystemNotification.objects.count(), 15)

        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 202)

        self.assertEqual(SystemNotification.objects.count(), 15)
        self.assertEqual(SystemNotification.objects.filter(is_read=False, user_id=self.user_2.pk).count(), 5)
        self.assertEqual(SystemNotification.objects.filter(is_read=False, user_id=self.user_3.pk).count(), 5)

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")
