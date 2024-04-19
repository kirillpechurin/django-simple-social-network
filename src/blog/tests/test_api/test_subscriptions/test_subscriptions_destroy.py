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
        self.subscription = Subscription.objects.create(to_user_id=self.user_1.pk, user_id=self.user_3.pk)

        self.client.force_authenticate(user=self.user_3, token=str(RefreshToken.for_user(self.user_3).access_token))

        self.url = f"/api/v1/blog/subscriptions/{self.subscription.pk}"


@tag("api-tests", "blog", "blog-subscriptions")
class SubscriptionDestroyAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 204)

    def test_response_data(self):
        resp = self.client.delete(self.url)
        self.assertEqual(resp.data, None)

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")

    def test_not_exists(self):
        resp = self.client.delete(f"/api/v1/blog/subscriptions/123")
        self.assertEqual(resp.status_code, 404)

    def test_use_filters(self):
        resp = self.client.delete(self.url + f"?user_id={self.user_1.pk}")
        self.assertEqual(resp.status_code, 404)

    def test_another_subscription(self):
        subscription = Subscription.objects.create(to_user_id=self.user_1.pk, user_id=self.user_2.pk)
        resp = self.client.delete(f"/api/v1/blog/subscriptions/{subscription.pk}")
        self.assertEqual(resp.status_code, 404)

    def test_only_current(self):
        Subscription.objects.create(to_user_id=self.user_1.pk, user_id=self.user_2.pk)
        Subscription.objects.create(to_user_id=self.user_2.pk, user_id=self.user_3.pk)
        Subscription.objects.create(to_user_id=self.user_3.pk, user_id=self.user_1.pk)

        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 204)

        self.assertEqual(Subscription.objects.count(), 3)
        self.assertTrue(Subscription.objects.filter(to_user_id=self.user_1.pk, user_id=self.user_2.pk).exists())
        self.assertTrue(Subscription.objects.filter(to_user_id=self.user_2.pk, user_id=self.user_3.pk).exists())
        self.assertTrue(Subscription.objects.filter(to_user_id=self.user_3.pk, user_id=self.user_1.pk).exists())
