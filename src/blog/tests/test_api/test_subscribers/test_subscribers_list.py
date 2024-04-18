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

        Subscription.objects.create(to_user_id=cls.user_1.pk, user_id=cls.user_2.pk)
        Subscription.objects.create(to_user_id=cls.user_1.pk, user_id=cls.user_3.pk)

        Subscription.objects.create(to_user_id=cls.user_2.pk, user_id=cls.user_3.pk)

        Subscription.objects.create(to_user_id=cls.user_3.pk, user_id=cls.user_1.pk)

    def setUp(self) -> None:
        super().setUp()

        self.client.force_authenticate(user=self.user_1, token=str(RefreshToken.for_user(self.user_1).access_token))

        self.url = "/api/v1/blog/subscribers"


@tag("api-tests", "blog", "blog-subscribers")
class SubscriberListAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_response_data(self):
        resp = self.client.get(self.url)
        self.assertIsInstance(resp.data, dict)
        data: dict = resp.data
        self.assertEqual(data["count"], self.user_1.subscribers.count())
        self.assertEqual(data["next"], None)
        self.assertEqual(data["previous"], None)
        self.assertEqual(len(data["results"]), 2)

        for item, subscriber in zip(resp.data["results"], self.user_1.subscribers.order_by("-created_at")):
            self.assertEqual(item.pop("id"), subscriber.pk)
            self.assertEqual(item.pop("from_user"), {
                "id": subscriber.user.pk,
                "username": subscriber.user.username
            })

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")


@tag("api-tests", "blog", "blog-subscriptions")
class SubscriberListFilterAPITestCase(_BaseTestCase):

    def test_by_to_user_id(self):
        resp = self.client.get(self.url, data={"to_user_id": self.user_2.pk})
        self.assertEqual(resp.data["count"], self.user_2.subscribers.count())
        self.assertEqual(resp.data["count"], 1)

        for item, subscription in zip(resp.data["results"], self.user_2.subscribers.order_by("-created_at")):
            self.assertEqual(item["id"], subscription.pk)

    def test_by_search(self):
        resp = self.client.get(self.url, data={"search": self.user_2.username})
        self.assertEqual(resp.data["count"], 1)

        user_4 = User.objects.create_user(email="test-4@gmail.com", username="test-4")
        user_5 = User.objects.create_user(email="test-5@gmail.com", username="test-5")

        Subscription.objects.create(to_user_id=user_4.pk, user_id=user_5.pk)

        resp = self.client.get(self.url, data={"search": user_4.username})
        self.assertEqual(resp.data["count"], 0)

        Subscription.objects.create(to_user_id=self.user_1.pk, user_id=user_4.pk)

        resp = self.client.get(self.url, data={"search": user_4.username})
        self.assertEqual(resp.data["count"], 1)


@tag("api-tests", "blog", "blog-subscriptions")
class SubscriberListOrderingFilterAPITestCase(_BaseTestCase):

    def test_by_created_at_asc(self):
        resp = self.client.get(self.url, data={"ordering": "created_at"})

        for item, subscriber in zip(resp.data["results"], self.user_1.subscribers.order_by("created_at")):
            self.assertEqual(item["id"], subscriber.pk)

    def test_by_created_at_desc(self):
        resp = self.client.get(self.url, data={"ordering": "-created_at"})

        for item, subscriber in zip(resp.data["results"], self.user_1.subscribers.order_by("-created_at")):
            self.assertEqual(item["id"], subscriber.pk)
