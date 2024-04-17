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

        self.url = "/api/v1/notifications/read"
        self.data = {
            "ids": list(SystemNotification.objects.filter(user_id=self.user_1.pk).values_list("id", flat=True)[0:3])
        }


@tag("api-tests", "notifications")
class SystemNotificationReadAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 202)

    def test_response_data(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.data, None)

    def test_entities(self):
        self.assertEqual(SystemNotification.objects.count(), 15)

        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 202)

        self.assertEqual(SystemNotification.objects.count(), 15)
        self.assertEqual(SystemNotification.objects.filter(is_read=True).count(), 3)

    def test_only_current_user(self):
        self.data["ids"] = list(SystemNotification.objects.filter(
            user_id=self.user_2.pk
        ).values_list("id", flat=True)[0:3])

        self.assertEqual(SystemNotification.objects.count(), 15)

        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 202)

        self.assertEqual(SystemNotification.objects.count(), 15)
        self.assertEqual(SystemNotification.objects.filter(is_read=True).count(), 0)

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")


@tag("api-tests", "notifications")
class SystemNotificationReadValidationAPITestCase(_BaseTestCase):

    def test_ids_exclude(self):
        self.data.pop("ids")
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["ids"][0]), "This field is required.")

    def test_ids_empty(self):
        self.data["ids"] = []
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["ids"][0]), "This list may not be empty.")

    def test_ids_invalid_inner(self):
        self.data["ids"] = ["invalid-1", "invalid-2"]
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["ids"][0][0]), "A valid integer is required.")
        self.assertEqual(str(resp.data["ids"][1][0]), "A valid integer is required.")
