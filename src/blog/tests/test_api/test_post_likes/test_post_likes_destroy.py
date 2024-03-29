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

        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 201)

        self.notifications_accept_mock.reset_mock()


@tag("api-tests", "blog", "posts", "post_likes")
class PostLikeDestroyAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 204)

    def test_response_data(self):
        resp = self.client.delete(self.url)
        self.assertEqual(resp.data, None)

    def test_entity(self):
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 204)

        self.assertEqual(PostLike.objects.count(), 0)

    def test_not_found_by_id(self):
        resp = self.client.delete("/api/v1/posts/123123/like")
        self.assertEqual(resp.status_code, 404)

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")

    def test_again(self):
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 204)

        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(str(resp.data["detail"]), "Not found.")

    def test_self_post(self):
        post = Post.objects.filter(user_id=self.user_1.pk).order_by("-created_at").first()
        url = f"/api/v1/posts/{post.pk}/like"
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(str(resp.data["detail"]), "You do not have permission to perform this action.")

    def test_delete_current(self):
        PostLike.objects.create(user_id=self.user_3.pk, post_id=self.post.pk)
        self.assertEqual(self.post.likes.count(), 2)

        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 204)

        self.assertEqual(self.post.likes.count(), 1)
        post_like = PostLike.objects.get()
        self.assertEqual(post_like.user_id, self.user_3.pk)
        self.assertEqual(post_like.post_id, self.post.pk)

    def test_mock(self):
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 204)

        self.notifications_accept_mock.assert_called_once_with(
            action="BLOG_POSTS_LIKE_REMOVE",
            data={
                "post_id": self.post.pk,
                "user_id": self.user_1.pk
            }
        )
