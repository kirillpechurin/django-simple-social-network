from django.test import tag
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from blog.models import Post
from users.models import User


class _BaseTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = User.objects.create_user(username="test-1")

    def setUp(self) -> None:
        super().setUp()

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
