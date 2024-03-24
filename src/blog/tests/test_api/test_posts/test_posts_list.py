from django.test import tag
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from blog.models import Post
from users.models import User


class _BaseTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user_1 = User.objects.create_user(username="test-1")
        cls.user_2 = User.objects.create_user(username="test-2")
        cls.user_3 = User.objects.create_user(username="test-3")
        for user in [cls.user_1, cls.user_2, cls.user_3]:
            for i in range(0, 5):
                Post.objects.create(user_id=user.pk, content=f"sample-{i}-{user.pk}")

    def setUp(self) -> None:
        super().setUp()

        self.client.force_authenticate(user=self.user_1, token=str(RefreshToken.for_user(self.user_1).access_token))

        self.url = "/api/v1/posts"


@tag("api-tests", "blog", "posts")
class PostListAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_response_data(self):
        resp = self.client.get(self.url)
        self.assertIsInstance(resp.data, dict)
        data: dict = resp.data
        self.assertEqual(data["count"], Post.objects.count())
        self.assertEqual(data["next"], 2)
        self.assertEqual(data["previous"], None)
        self.assertEqual(len(data["results"]), 10)

        for item, post in zip(resp.data["results"], Post.objects.order_by("-created_at")):
            self.assertEqual(item.pop("id"), post.pk)
            self.assertEqual(item.pop("content"), post.content)
            self.assertIsNotNone(item.pop("created_at"))
            self.assertIsNotNone(item.pop("updated_at"))

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")


@tag("api-tests", "blog", "posts")
class PostListFilterAPITestCase(_BaseTestCase):

    def test_by_only_from_me(self):
        resp = self.client.get(self.url, data={"only_from_me": "true"})
        self.assertEqual(resp.data["count"], Post.objects.filter(user_id=self.user_1.pk).count())

        for item, post in zip(resp.data["results"], Post.objects.filter(
                user_id=self.user_1.pk
        ).order_by("-created_at")):
            self.assertEqual(item["id"], post.pk)

    def test_by_search(self):
        resp = self.client.get(self.url, data={"search": f"SAMPLE-{self.user_1.pk}"})
        self.assertEqual(resp.data["count"], Post.objects.filter(content__icontains=f"sample-{self.user_1.pk}").count())

        for item, post in zip(resp.data["results"], Post.objects.filter(
                content__icontains=f"sample-{self.user_1.pk}"
        ).order_by("-created_at")):
            self.assertEqual(item["id"], post.pk)


@tag("api-tests", "blog", "posts")
class PostListOrderingFilterAPITestCase(_BaseTestCase):

    def test_by_created_at_asc(self):
        resp = self.client.get(self.url, data={"ordering": "created_at"})

        for item, post in zip(resp.data["results"], Post.objects.order_by("created_at")):
            self.assertEqual(item["id"], post.pk)

    def test_by_created_at_desc(self):
        resp = self.client.get(self.url, data={"ordering": "-created_at"})

        for item, post in zip(resp.data["results"], Post.objects.order_by("-created_at")):
            self.assertEqual(item["id"], post.pk)
