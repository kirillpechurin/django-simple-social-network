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
        self.data = {
            "content": "new-sample-content"
        }


@tag("api-tests", "blog", "posts")
class PostUpdateAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.patch(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

    def test_response_data(self):
        resp = self.client.patch(self.url, data=self.data)
        self.assertIsInstance(resp.data, dict)
        data: dict = resp.data

        self.post.refresh_from_db()
        self.assertEqual(data.pop("id"), self.post.pk)
        self.assertEqual(data.pop("content"), self.post.content)
        self.assertIsNotNone(data.pop("created_at"))
        self.assertIsNotNone(data.pop("updated_at"))

    def test_entity(self):
        resp = self.client.patch(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

        self.post.refresh_from_db()
        self.assertEqual(self.post.content, self.data["content"])

    def test_not_found_by_id(self):
        resp = self.client.patch("/api/v1/posts/123123", data=self.data)
        self.assertEqual(resp.status_code, 404)

    def test_try_edit_not_self_post(self):
        user = User.objects.create_user(email="test-2@gmail.com", username="test-2")
        client = self.client_class()
        client.force_authenticate(user=user, token=str(RefreshToken.for_user(user).access_token))

        resp = client.patch(self.url, data=self.data)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(str(resp.data["detail"]), "You do not have permission to perform this action.")

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.patch(self.url, data=self.data)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")


@tag("api-tests", "blog", "posts")
class PostUpdateValidationAPITestCase(_BaseTestCase):

    def test_content_empty(self):
        self.data["content"] = ""
        resp = self.client.patch(self.url, data=self.data)
        self.assertEqual(str(resp.data["content"][0]), "This field may not be blank.")

    def test_content_exclude(self):
        self.data.pop("content")
        resp = self.client.patch(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

    def test_content_null(self):
        self.data["content"] = None
        resp = self.client.patch(self.url, data=self.data)
        self.assertEqual(str(resp.data["content"][0]), "This field may not be null.")

    def test_content_more_than_500(self):
        self.data["content"] = "1" * 501
        resp = self.client.patch(self.url, data=self.data)
        self.assertEqual(str(resp.data["content"][0]), "Ensure this field has no more than 500 characters.")
