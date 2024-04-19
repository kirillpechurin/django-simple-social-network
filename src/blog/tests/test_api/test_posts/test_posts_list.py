from django.test import tag
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from blog.models import Post, PostLike, Subscription
from users.models import User


class _BaseTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user_1 = User.objects.create_user(email="test-1@gmail.com", username="test-1")
        cls.user_2 = User.objects.create_user(email="test-2@gmail.com", username="test-2")
        cls.user_3 = User.objects.create_user(email="test-3@gmail.com", username="test-3")
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

    def test_with_likes(self):
        PostLike.objects.bulk_create([
            PostLike(
                user_id=user.pk,
                post_id=post.pk
            )
            for user in [self.user_1, self.user_2, self.user_3]
            for post in Post.objects.all()
            if user.pk != post.user_id
        ])

        resp = self.client.get(self.url + "?count=100")
        for item, post in zip(resp.data["results"], Post.objects.order_by("-created_at")):
            self.assertEqual(item["id"], post.pk)
            self.assertEqual(item["count_likes"], post.likes.count())
            self.assertTrue(post.likes.count(), 2)


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

    def _create_subscriptions(self):
        Subscription.objects.create(to_user_id=self.user_1.pk, user_id=self.user_2.pk)

        Subscription.objects.create(to_user_id=self.user_2.pk, user_id=self.user_3.pk)

        Subscription.objects.create(to_user_id=self.user_3.pk, user_id=self.user_1.pk)

    def test_by_from_subscriptions_asc(self):
        self._create_subscriptions()
        resp = self.client.get(self.url, data={"ordering": "from_subscriptions"})
        self.assertEqual(resp.data["count"], 15)

        posts_from_user_3 = Post.objects.filter(user_id=self.user_3.pk).order_by("-created_at")
        for item, post in zip(resp.data["results"][0:10], Post.objects.exclude(
            id__in=posts_from_user_3.values_list("id", flat=True)
        ).order_by("-created_at")):
            self.assertEqual(item["id"], post.pk)

        for item, post in zip(resp.data["results"][10:], posts_from_user_3):
            self.assertEqual(item["id"], post.pk)
        self.assertEqual(posts_from_user_3.count(), 5)

        client_2 = self.client_class()
        client_2.force_authenticate(user=self.user_2, token=str(RefreshToken.for_user(self.user_2).access_token))
        resp = client_2.get(self.url, data={"ordering": "from_subscriptions"})
        self.assertEqual(resp.data["count"], 15)

        posts_from_user_1 = Post.objects.filter(user_id=self.user_1.pk).order_by("-created_at")
        for item, post in zip(resp.data["results"][0:10], Post.objects.exclude(
                id__in=posts_from_user_1.values_list("id", flat=True)
        ).order_by("-created_at")):
            self.assertEqual(item["id"], post.pk)

        for item, post in zip(resp.data["results"][10:], posts_from_user_1):
            self.assertEqual(item["id"], post.pk)
        self.assertEqual(posts_from_user_1.count(), 5)

        client_3 = self.client_class()
        client_3.force_authenticate(user=self.user_3, token=str(RefreshToken.for_user(self.user_3).access_token))
        resp = client_3.get(self.url, data={"ordering": "from_subscriptions"})
        self.assertEqual(resp.data["count"], 15)

        posts_from_user_2 = Post.objects.filter(user_id=self.user_2.pk).order_by("-created_at")
        for item, post in zip(resp.data["results"][0:10], Post.objects.exclude(
                id__in=posts_from_user_2.values_list("id", flat=True)
        ).order_by("-created_at")):
            self.assertEqual(item["id"], post.pk)

        for item, post in zip(resp.data["results"][10:], posts_from_user_2):
            self.assertEqual(item["id"], post.pk)
        self.assertEqual(posts_from_user_2.count(), 5)

    def test_by_from_subscriptions_desc(self):
        self._create_subscriptions()
        resp = self.client.get(self.url, data={"ordering": "-from_subscriptions"})
        self.assertEqual(resp.data["count"], 15)

        posts_from_user_3 = Post.objects.filter(user_id=self.user_3.pk).order_by("-created_at")
        for item, post in zip(resp.data["results"], posts_from_user_3):
            self.assertEqual(item["id"], post.pk)
        self.assertEqual(posts_from_user_3.count(), 5)

        for item, post in zip(resp.data["results"][5:], Post.objects.exclude(
            id__in=posts_from_user_3.values_list("id", flat=True)
        ).order_by("-created_at")):
            self.assertEqual(item["id"], post.pk)

        client_2 = self.client_class()
        client_2.force_authenticate(user=self.user_2, token=str(RefreshToken.for_user(self.user_2).access_token))
        resp = client_2.get(self.url, data={"ordering": "-from_subscriptions"})
        self.assertEqual(resp.data["count"], 15)

        posts_from_user_1 = Post.objects.filter(user_id=self.user_1.pk).order_by("-created_at")
        for item, post in zip(resp.data["results"], posts_from_user_1):
            self.assertEqual(item["id"], post.pk)
        self.assertEqual(posts_from_user_1.count(), 5)

        for item, post in zip(resp.data["results"][5:], Post.objects.exclude(
                id__in=posts_from_user_1.values_list("id", flat=True)
        ).order_by("-created_at")):
            self.assertEqual(item["id"], post.pk)

        client_3 = self.client_class()
        client_3.force_authenticate(user=self.user_3, token=str(RefreshToken.for_user(self.user_3).access_token))
        resp = client_3.get(self.url, data={"ordering": "-from_subscriptions"})
        self.assertEqual(resp.data["count"], 15)

        posts_from_user_2 = Post.objects.filter(user_id=self.user_2.pk).order_by("-created_at")
        for item, post in zip(resp.data["results"], posts_from_user_2):
            self.assertEqual(item["id"], post.pk)
        self.assertEqual(posts_from_user_2.count(), 5)

        for item, post in zip(resp.data["results"][5:], Post.objects.exclude(
                id__in=posts_from_user_2.values_list("id", flat=True)
        ).order_by("-created_at")):
            self.assertEqual(item["id"], post.pk)
