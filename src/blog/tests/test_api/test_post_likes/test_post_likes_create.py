from django.test import tag
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from blog.models import Post, PostLike
from common.tests.mixins import MockTestCaseMixin
from users.models import User


class _BaseTestCase(APITestCase,
                    MockTestCaseMixin):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user_1 = User.objects.create_user(username="test-1")
        cls.user_2 = User.objects.create_user(username="test-2")
        cls.user_3 = User.objects.create_user(username="test-3")
        for user in [cls.user_1, cls.user_2, cls.user_3]:
            for i in range(0, 2):
                Post.objects.create(user_id=user.pk, content=f"sample-{i}-{user.pk}")

    def setUp(self) -> None:
        super().setUp()

        self.client.force_authenticate(user=self.user_1, token=str(RefreshToken.for_user(self.user_1).access_token))

        self.post = Post.objects.filter(user_id=self.user_2.pk).order_by("-created_at").first()
        self.url = f"/api/v1/posts/{self.post.pk}/like"

        self.notifications_accept_mock = self._mock(
            "notifications.entrypoint.Handler.accept"
        )


@tag("api-tests", "blog", "posts", "post_likes")
class PostLikeCreateAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 201)

    def test_response_data(self):
        resp = self.client.post(self.url)
        self.assertEqual(resp.data, None)

    def test_entity(self):
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 201)

        self.assertEqual(self.post.likes.count(), 1)

        self.assertEqual(PostLike.objects.count(), 1)
        post_like = PostLike.objects.get()
        self.assertEqual(post_like.user_id, self.user_1.pk)
        self.assertEqual(post_like.post_id, self.post.pk)

    def test_not_found_by_id(self):
        resp = self.client.delete("/api/v1/posts/123123/like")
        self.assertEqual(resp.status_code, 404)

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")

    def test_again(self):
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 201)

        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(str(resp.data["detail"]), "You do not have permission to perform this action.")

    def test_cannot_like_self_post(self):
        post = Post.objects.filter(user_id=self.user_1.pk).order_by("-created_at").first()
        url = f"/api/v1/posts/{post.pk}/like"
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(str(resp.data["detail"]), "You do not have permission to perform this action.")

    def test_mock(self):
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 201)

        self.notifications_accept_mock.assert_called_once_with(
            action="BLOG_POSTS_LIKE",
            data={
                "post": {
                    "id": self.post.pk,
                    "user_id": self.post.user_id
                },
                "from_user": {
                    "id": self.user_1.pk
                }
            }
        )
