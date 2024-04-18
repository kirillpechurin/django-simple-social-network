from django.test import tag
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from blog.models import Post, Subscription
from users.models import User


class _BaseTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user_1 = User.objects.create_user(
            email="test-1@gmail.com",
            username="test-1",
            personal_website_url="http://example-1.com"
        )
        cls.user_2 = User.objects.create_user(
            email="test-2@gmail.com",
            username="test-2",
            personal_website_url="http://example-2.com"
        )
        cls.user_3 = User.objects.create_user(
            email="test-3@gmail.com",
            username="test-3",
            personal_website_url="http://example-3.com"
        )
        for user in [cls.user_1, cls.user_2, cls.user_3]:
            for i in range(0, 5):
                Post.objects.create(user_id=user.pk, content=f"sample-{i}-{user.pk}")

        Subscription.objects.create(to_user_id=cls.user_1.pk, user_id=cls.user_2.pk)
        Subscription.objects.create(to_user_id=cls.user_1.pk, user_id=cls.user_3.pk)

        Subscription.objects.create(to_user_id=cls.user_2.pk, user_id=cls.user_3.pk)

        Subscription.objects.create(to_user_id=cls.user_3.pk, user_id=cls.user_1.pk)

    def setUp(self) -> None:
        super().setUp()

        self.client.force_authenticate(user=self.user_3, token=str(RefreshToken.for_user(self.user_3).access_token))

        self.url = f"/api/v1/blog/users/{self.user_1.pk}"


@tag("api-tests", "blog", "blog-users")
class BlogUserRetrieveAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_response_data(self):
        resp = self.client.get(self.url)
        self.assertIsInstance(resp.data, dict)
        data: dict = resp.data

        self.assertEqual(data.pop("id"), self.user_1.id)
        self.assertEqual(data.pop("username"), self.user_1.username)
        self.assertEqual(data.pop("personal_website_url"), self.user_1.personal_website_url)
        self.assertEqual(data.pop("count_posts"), self.user_1.posts.count())
        self.assertEqual(self.user_1.posts.count(), 5)
        self.assertEqual(data.pop("count_subscribers"), self.user_1.subscribers.count())
        self.assertEqual(self.user_1.subscribers.count(), 2)
        self.assertEqual(data.pop("count_subscriptions"), self.user_1.subscriptions.count())
        self.assertEqual(self.user_1.subscriptions.count(), 1)

        self.assertEqual(data, {})

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")

    def test_count_posts(self):
        Post.objects.create(user_id=self.user_3.pk, content=f"sample-post-1")

        resp = self.client.get(self.url)
        self.assertEqual(resp.data["count_posts"], 5)

        Post.objects.create(user_id=self.user_1.pk, content=f"sample-post-1")

        resp = self.client.get(self.url)
        self.assertEqual(resp.data["count_posts"], 6)

    def test_count_subscribers(self):
        user_4 = User.objects.create_user(email="test-4@gmail.com", username="test-4")
        user_5 = User.objects.create_user(email="test-5@gmail.com", username="test-5")

        Subscription.objects.create(to_user_id=user_4.pk, user_id=user_5.pk)

        resp = self.client.get(self.url)
        self.assertEqual(resp.data["count_subscribers"], 2)

        Subscription.objects.create(to_user_id=user_5.pk, user_id=self.user_1.pk)

        resp = self.client.get(self.url)
        self.assertEqual(resp.data["count_subscribers"], 2)

        Subscription.objects.create(to_user_id=self.user_1.pk, user_id=user_5.pk)

        resp = self.client.get(self.url)
        self.assertEqual(resp.data["count_subscribers"], 3)

    def test_count_subscriptions(self):
        user_4 = User.objects.create_user(email="test-4@gmail.com", username="test-4")
        user_5 = User.objects.create_user(email="test-5@gmail.com", username="test-5")

        Subscription.objects.create(to_user_id=user_4.pk, user_id=user_5.pk)

        resp = self.client.get(self.url)
        self.assertEqual(resp.data["count_subscriptions"], 1)

        Subscription.objects.create(to_user_id=self.user_1.pk, user_id=user_5.pk)

        resp = self.client.get(self.url)
        self.assertEqual(resp.data["count_subscriptions"], 1)

        Subscription.objects.create(to_user_id=user_5.pk, user_id=self.user_1.pk)

        resp = self.client.get(self.url)
        self.assertEqual(resp.data["count_subscriptions"], 2)
