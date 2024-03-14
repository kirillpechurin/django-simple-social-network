import datetime

from django.conf import settings
from django.test import tag
from rest_framework.test import APITestCase
from rest_framework_simplejwt.settings import api_settings as simple_jwt_settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.utils import aware_utcnow, datetime_from_epoch

from users.models import User


class _BaseTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = User.objects.create_user(
            username="test",
            email="example@gmail.com",
            password="test-password"
        )
        cls.refresh_token = RefreshToken.for_user(cls.user)
        cls.access_token = cls.refresh_token.access_token

    def setUp(self) -> None:
        super().setUp()

        self.client = self.client_class()

        self.url = "/api/v1/auth/logout"
        self.data = {
            "refresh": str(self.refresh_token),
        }


@tag("api-tests", "auth")
class AuthLogoutAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

    def test_response_data(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.data, {})

    def test_user_is_not_active(self):
        user = User.objects.create_user(
            username="test-2",
            email="example-2@gmail.com",
            password="sample-2",
            is_active=False
        )
        self.data["refresh"] = str(RefreshToken.for_user(user))
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

    def test_use_again(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)


@tag("api-tests", "auth")
class AuthLogoutValidationAPITestCase(_BaseTestCase):

    def test_refresh_empty(self):
        self.data["refresh"] = ""
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

    def test_refresh_exclude(self):
        self.data.pop("refresh")
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

    def test_refresh_null(self):
        self.data["refresh"] = None
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

    def test_refresh_invalid(self):
        self.data["refresh"] = "invalid"
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)
