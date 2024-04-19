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
        user_ids = [item.pk for item in [cls.user_1, cls.user_2, cls.user_3]]
        for user in [cls.user_1, cls.user_2, cls.user_3]:
            for i in range(0, 2):
                post = Post.objects.create(user_id=user.pk, content=f"sample-{i}-{user.pk}")
                PostComment.objects.bulk_create([
                    PostComment(
                        user_id=user_id,
                        post_id=post.pk,
                        comment=f"sample-comment-{i}-{user.pk}"
                    )
                    for user_id in set(user_ids) - {user.pk}
                ])

    def setUp(self) -> None:
        super().setUp()

        self.client.force_authenticate(user=self.user_1, token=str(RefreshToken.for_user(self.user_1).access_token))

        self.post = Post.objects.filter(user_id=self.user_2.pk).order_by("-created_at").first()
        self.url = f"/api/v1/posts/{self.post.pk}/comments"


@tag("api-tests", "blog", "posts", "post_comments")
class PostCommentListAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_response_data(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.data["count"], 2)
        self.assertEqual(resp.data["next"], None)
        self.assertEqual(resp.data["previous"], None)
        self.assertEqual(len(resp.data["results"]), 2)

        for item, comment in zip(resp.data["results"], PostComment.objects.filter(
            post_id=self.post.pk
        ).order_by("-created_at")):
            self.assertEqual(item.pop("id"), comment.pk)
            self.assertEqual(item.pop("from_user"), {
                "id": comment.user_id,
                "username": comment.user.username
            })
            self.assertEqual(item.pop("comment"), comment.comment)
            self.assertEqual(item, {})

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")


@tag("api-tests", "blog", "posts")
class PostCommentListOrderingFilterAPITestCase(_BaseTestCase):

    def test_by_created_at_asc(self):
        resp = self.client.get(self.url, data={"ordering": "created_at"})

        for item, comment in zip(resp.data["results"], PostComment.objects.filter(
                post_id=self.post.pk
        ).order_by("created_at")):
            self.assertEqual(item["id"], comment.pk)

    def test_by_created_at_desc(self):
        resp = self.client.get(self.url, data={"ordering": "-created_at"})

        for item, comment in zip(resp.data["results"], PostComment.objects.filter(
                post_id=self.post.pk
        ).order_by("-created_at")):
            self.assertEqual(item["id"], comment.pk)
