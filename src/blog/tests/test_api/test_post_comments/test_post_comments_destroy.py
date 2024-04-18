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

        self.notifications_accept_mock = self._mock(
            "notifications.entrypoint.Handler.accept"
        )

        self.client.force_authenticate(user=self.user_1, token=str(RefreshToken.for_user(self.user_1).access_token))

        self.post = Post.objects.filter(user_id=self.user_2.pk).order_by("-created_at").first()
        self.client.post(f"/api/v1/posts/{self.post.pk}/comments", data={
            "comment": "test-comment"
        })
        self.comment = PostComment.objects.get()

        self.url = f"/api/v1/posts/{self.post.pk}/comments/{self.comment.pk}"


@tag("api-tests", "blog", "posts", "post_comments")
class PostCommentDestroyAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 204)

    def test_response_data(self):
        resp = self.client.delete(self.url)
        self.assertEqual(resp.data, None)

    def test_entity(self):
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 204)

        self.assertEqual(PostComment.objects.count(), 0)

    def test_not_found_by_post_id(self):
        resp = self.client.delete(f"/api/v1/posts/123123/comments/{self.comment.pk}")
        self.assertEqual(resp.status_code, 404)

    def test_not_found_by_id(self):
        resp = self.client.delete(f"/api/v1/posts/{self.post.pk}/comments/123")
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

    def test_comment_no_owner(self):
        self.client.force_authenticate(user=self.user_2, token=str(RefreshToken.for_user(self.user_2).access_token))
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(str(resp.data["detail"]), "You do not have permission to perform this action.")

    def test_delete_current(self):
        PostComment.objects.create(user_id=self.user_3.pk, post_id=self.post.pk, comment="test-comment-3")
        self.assertEqual(self.post.comments.count(), 2)

        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 204)

        self.assertEqual(self.post.comments.count(), 1)
        post_comment = PostComment.objects.get()
        self.assertEqual(post_comment.user_id, self.user_3.pk)
        self.assertEqual(post_comment.post_id, self.post.pk)
        self.assertEqual(post_comment.comment, "test-comment-3")
