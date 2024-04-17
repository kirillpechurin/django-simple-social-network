from django.test import tag
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from blog.models import Post
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
class PostDestroyAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 204)

    def test_response_data(self):
        resp = self.client.delete(self.url)
        self.assertEqual(resp.data, None)

    def test_entity(self):
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 204)

        self.assertEqual(Post.objects.count(), 0)

    def test_not_found_by_id(self):
        resp = self.client.delete("/api/v1/posts/123123")
        self.assertEqual(resp.status_code, 404)

    def test_try_delete_not_self_post(self):
        user = User.objects.create_user(email="test-2@gmail.com", username="test-2")
        client = self.client_class()
        client.force_authenticate(user=user, token=str(RefreshToken.for_user(user).access_token))

        resp = client.delete(self.url)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(str(resp.data["detail"]), "You do not have permission to perform this action.")

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")
