from django.test import tag
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from blog.models import Post, Subscription
from common.tests.mixins import MockTestCaseMixin
from users.models import User


class _BaseTestCase(APITestCase,
                    MockTestCaseMixin):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = User.objects.create_user(email="test-1@gmail.com", username="test-1")

    def setUp(self) -> None:
        super().setUp()

        self.notifications_accept_mock = self._mock(
            "notifications.entrypoint.Handler.accept"
        )

        self.client.force_authenticate(user=self.user, token=str(RefreshToken.for_user(self.user).access_token))

        self.url = "/api/v1/posts"
        self.data = {
            "content": "sample"
        }


@tag("api-tests", "blog", "posts")
class PostCreateAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 201)

    def test_response_data(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertIsInstance(resp.data, dict)
        data: dict = resp.data

        post = Post.objects.get()
        self.assertEqual(data.pop("id"), post.pk)
        self.assertEqual(data.pop("content"), post.content)
        self.assertEqual(data.pop("count_likes"), post.likes.count())
        self.assertIsNotNone(data.pop("created_at"))
        self.assertIsNotNone(data.pop("updated_at"))

        self.assertEqual(data, {})

    def test_entity(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 201)

        post = Post.objects.get()
        self.assertEqual(post.content, self.data["content"])
        self.assertEqual(post.user_id, self.user.pk)

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")

    def test_mock_default(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 201)

        self.notifications_accept_mock.assert_not_called()

    def test_mock_with_subscribers(self):
        user_1 = self.user
        user_2 = User.objects.create_user(email="test-2@gmail.com", username="test-2")
        user_3 = User.objects.create_user(email="test-3@gmail.com", username="test-3")

        Subscription.objects.create(to_user_id=user_1.pk, user_id=user_2.pk)
        Subscription.objects.create(to_user_id=user_1.pk, user_id=user_3.pk)
        Subscription.objects.create(to_user_id=user_2.pk, user_id=user_3.pk)
        Subscription.objects.create(to_user_id=user_3.pk, user_id=user_1.pk)

        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 201)
        post = Post.objects.get(id=resp.data["id"])
        self.notifications_accept_mock.assert_called_once_with(
            action="BLOG_POSTS_NEW",
            data={
                "post": {
                    "id": post.pk,
                    "user": {
                        "id": self.user.pk,
                        "username": self.user.username
                    }
                },
                "to_user_ids": [user_2.pk, user_3.pk]
            }
        )

        self.notifications_accept_mock.reset_mock()

        user_4 = User.objects.create_user(email="test-4@gmail.com", username="test-4")
        user_5 = User.objects.create_user(email="test-5@gmail.com", username="test-5")

        Subscription.objects.create(to_user_id=user_4.pk, user_id=user_5.pk)
        Subscription.objects.create(to_user_id=user_1.pk, user_id=user_4.pk)
        Subscription.objects.filter(to_user_id=user_1.pk, user_id=user_2.pk).delete()

        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 201)
        post = Post.objects.get(id=resp.data["id"])
        self.notifications_accept_mock.assert_called_once_with(
            action="BLOG_POSTS_NEW",
            data={
                "post": {
                    "id": post.pk,
                    "user": {
                        "id": self.user.pk,
                        "username": self.user.username
                    }
                },
                "to_user_ids": [user_3.pk, user_4.pk]
            }
        )


@tag("api-tests", "blog", "posts")
class PostCreateValidationAPITestCase(_BaseTestCase):

    def test_content_empty(self):
        self.data["content"] = ""
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(str(resp.data["content"][0]), "This field may not be blank.")

    def test_content_exclude(self):
        self.data.pop("content")
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(str(resp.data["content"][0]), "This field is required.")

    def test_content_null(self):
        self.data["content"] = None
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(str(resp.data["content"][0]), "This field may not be null.")

    def test_content_more_than_500(self):
        self.data["content"] = "1" * 501
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(str(resp.data["content"][0]), "Ensure this field has no more than 500 characters.")
