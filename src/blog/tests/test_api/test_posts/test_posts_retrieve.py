from django.test import tag
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from blog.models import Post, PostLike
from users.models import User


class _BaseTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = User.objects.create_user(email="test-1@gmail.com", username="test-1")

        cls.post = Post.objects.create(user_id=cls.user.pk, content=f"sample-content")

    def setUp(self) -> None:
        super().setUp()

        self.client.force_authenticate(user=self.user, token=str(RefreshToken.for_user(self.user).access_token))

        self.url = f"/api/v1/posts/{self.post.pk}"


@tag("api-tests", "blog", "posts")
class PostRetrieveAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_response_data(self):
        resp = self.client.get(self.url)
        self.assertIsInstance(resp.data, dict)
        data: dict = resp.data

        self.assertEqual(data.pop("id"), self.post.pk)
        self.assertEqual(data.pop("content"), self.post.content)
        self.assertIsNotNone(data.pop("created_at"))
        self.assertIsNotNone(data.pop("updated_at"))

    def test_not_found_by_id(self):
        resp = self.client.get("/api/v1/posts/123123")
        self.assertEqual(resp.status_code, 404)

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")

    def test_with_likes(self):
        user_2 = User.objects.create_user(email="test-2@gmail.com", username="test-2")
        user_3 = User.objects.create_user(email="test-3@gmail.com", username="test-3")
        PostLike.objects.bulk_create([
            PostLike(
                user_id=user.pk,
                post_id=self.post.pk
            )
            for user in [user_2, user_3]
        ])

        resp = self.client.get(self.url)
        self.assertEqual(resp.data["id"], self.post.pk)
        self.assertEqual(resp.data["count_likes"], self.post.likes.count())
        self.assertEqual(resp.data["count_likes"], 2)
