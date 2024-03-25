from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


class _BaseTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.test_password = "test-password"
        cls.user = User.objects.create_user(
            username="test",
            email="example@gmail.com",
            password="test-password",
            first_name="John",
            last_name="Doe",
            personal_website_url="https://example.com",
            address="sample address"
        )

    def setUp(self) -> None:
        super().setUp()

        self.client.force_authenticate(user=self.user, token=str(RefreshToken.for_user(self.user).access_token))

        self.url = "/api/v1/account"


class AccountAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_response_data(self):
        resp = self.client.get(self.url)
        self.assertIsInstance(resp.data, dict)

        data: dict = resp.data
        self.assertEqual(data.pop("id"), self.user.id)
        self.assertEqual(data.pop("first_name"), self.user.first_name)
        self.assertEqual(data.pop("last_name"), self.user.last_name)
        self.assertEqual(data.pop("username"), self.user.username)
        self.assertEqual(data.pop("email"), self.user.email)
        self.assertEqual(data.pop("personal_website_url"), self.user.personal_website_url)
        self.assertEqual(data.pop("address"), self.user.address)

        self.assertEqual(data, {})

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")
