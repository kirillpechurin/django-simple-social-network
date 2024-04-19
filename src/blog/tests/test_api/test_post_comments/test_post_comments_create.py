from django.test import tag
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from blog.models import Post, PostComment
from common.tests.mixins import MockTestCaseMixin
from users.models import User


class _BaseTestCase(APITestCase,
                    MockTestCaseMixin):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user_1 = User.objects.create_user(email="test-1@gmail.com", username="test-1")
        cls.user_2 = User.objects.create_user(email="test-2@gmail.com", username="test-2")
        cls.user_3 = User.objects.create_user(email="test-3@gmail.com", username="test-3")
        for user in [cls.user_1, cls.user_2, cls.user_3]:
            for i in range(0, 2):
                Post.objects.create(user_id=user.pk, content=f"sample-{i}-{user.pk}")

    def setUp(self) -> None:
        super().setUp()

        self.client.force_authenticate(user=self.user_1, token=str(RefreshToken.for_user(self.user_1).access_token))

        self.post = Post.objects.filter(user_id=self.user_2.pk).order_by("-created_at").first()
        self.url = f"/api/v1/posts/{self.post.pk}/comments"
        self.data = {
            "comment": "test-comment"
        }

        self.notifications_accept_mock = self._mock(
            "notifications.entrypoint.Handler.accept"
        )


@tag("api-tests", "blog", "posts", "post_comments")
class PostCommentCreateAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 201)

    def test_response_data(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertIsInstance(resp.data, dict)
        data: dict = resp.data
        comment = PostComment.objects.get()
        self.assertEqual(data.pop("id"), comment.pk)
        self.assertEqual(data.pop("from_user"), {
            "id": comment.user_id,
            "username": comment.user.username
        })
        self.assertEqual(data.pop("comment"), self.data["comment"])

        self.assertEqual(data, {})

    def test_entity(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 201)

        self.assertEqual(self.post.comments.count(), 1)

        self.assertEqual(PostComment.objects.count(), 1)
        post_comment = PostComment.objects.get()
        self.assertEqual(post_comment.user_id, self.user_1.pk)
        self.assertEqual(post_comment.post_id, self.post.pk)
        self.assertEqual(post_comment.comment, self.data["comment"])

    def test_not_found_by_id(self):
        resp = self.client.delete("/api/v1/posts/123123/comments")
        self.assertEqual(resp.status_code, 404)

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")

    def test_again(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 201)

        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 201)

    def test_cannot_comment_self_post(self):
        post = Post.objects.filter(user_id=self.user_1.pk).order_by("-created_at").first()
        url = f"/api/v1/posts/{post.pk}/comments"
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(str(resp.data["detail"]), "You do not have permission to perform this action.")

    def test_mock(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 201)

        self.notifications_accept_mock.assert_called_once_with(
            action="BLOG_POSTS_NEW_COMMENT",
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
