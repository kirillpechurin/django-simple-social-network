from django.test import tag
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from blog.models import Subscription
from users.models import User


class _BaseTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user_1 = User.objects.create_user(email="test-1@gmail.com", username="test-1")
        cls.user_2 = User.objects.create_user(email="test-2@gmail.com", username="test-2")
        cls.user_3 = User.objects.create_user(email="test-3@gmail.com", username="test-3")

    def setUp(self) -> None:
        super().setUp()

        self.client.force_authenticate(user=self.user_3, token=str(RefreshToken.for_user(self.user_3).access_token))

        self.url = "/api/v1/blog/subscriptions"
        self.data = {
            "to_user_id": self.user_1.pk
        }


@tag("api-tests", "blog", "blog-subscriptions")
class SubscriptionCreateAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 201)

    def test_response_data(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.data, None)

    def test_entity(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 201)

        subscription = Subscription.objects.get()
        self.assertEqual(subscription.to_user_id, self.data["to_user_id"])
        self.assertEqual(subscription.user_id, self.user_3.pk)

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")

    def test_again(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 201)

        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(str(resp.data["detail"]), "You have already subscribed.")

    def test_try_self(self):
        self.data = {
            "to_user_id": self.user_3.pk
        }
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(str(resp.data["detail"]), "You do not have permission to perform this action.")

    def test_try_not_exists_to_user_id(self):
        self.data = {
            "to_user_id": 123
        }
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(str(resp.data["detail"]), "You do not have permission to perform this action.")


@tag("api-tests", "blog", "blog-subscriptions")
class SubscriptionCreateValidationAPITestCase(_BaseTestCase):

    def test_to_user_id_null(self):
        self.data["to_user_id"] = None
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["to_user_id"][0]), "This field may not be null.")

    def test_to_user_id_exclude(self):
        self.data.pop("to_user_id")
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["to_user_id"][0]), "This field is required.")

    def test_to_user_id_empty(self):
        self.data["to_user_id"] = ""
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["to_user_id"][0]), "A valid integer is required.")
