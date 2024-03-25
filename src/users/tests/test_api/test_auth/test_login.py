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

        cls.test_password = "test-password"
        cls.user = User.objects.create_user(
            username="test",
            email="example@gmail.com",
            password=cls.test_password
        )

    def setUp(self) -> None:
        super().setUp()

        self.client = self.client_class()

        self.url = "/api/v1/auth/login"
        self.data = {
            "username": self.user.username,
            "password": self.test_password
        }


@tag("api-tests", "auth")
class AuthLoginAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

    def test_response_data(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertIsInstance(resp.data, dict)
        data: dict = resp.data
        self.assertIsNotNone(data.pop("refresh"))
        self.assertIsNotNone(data.pop("access"))
        self.assertEqual(len(data.keys()), 0)

    def _check_token_exp(self, validated_token, timedelta: datetime.timedelta):
        current_time = aware_utcnow()
        claim_time = datetime_from_epoch(validated_token.payload["exp"])

        self.assertEqual(claim_time < current_time + timedelta, True)
        self.assertEqual(claim_time > current_time, True)

        current_time = aware_utcnow()
        iat_time = datetime_from_epoch(validated_token.payload["iat"])
        self.assertEqual(
            iat_time < current_time, True
        )

    def test_access_entity(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

        access = resp.data["access"]
        validated_token = AccessToken(access)
        self.assertEqual(validated_token.payload["token_type"], "access")
        self.assertEqual(
            settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            simple_jwt_settings.ACCESS_TOKEN_LIFETIME
        )
        self._check_token_exp(validated_token, timedelta=simple_jwt_settings.ACCESS_TOKEN_LIFETIME)
        self.assertEqual(validated_token.payload["user_id"], self.user.pk)
        self.assertIsNotNone(validated_token.payload["jti"])
        self.assertEqual(len(validated_token.payload.keys()), 5)

    def test_refresh_entity(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

        refresh = resp.data["refresh"]
        validated_token = RefreshToken(refresh)
        self.assertEqual(validated_token.payload["token_type"], "refresh")
        self.assertEqual(
            settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            simple_jwt_settings.REFRESH_TOKEN_LIFETIME
        )
        self._check_token_exp(validated_token, timedelta=simple_jwt_settings.REFRESH_TOKEN_LIFETIME)
        self.assertEqual(validated_token.payload["user_id"], self.user.pk)
        self.assertIsNotNone(validated_token.payload["jti"])
        self.assertEqual(len(validated_token.payload.keys()), 5)

    def test_user_is_not_active(self):
        user = User.objects.create_user(
            username="test-2",
            email="example-2@gmail.com",
            password="sample-2",
            is_active=False
        )
        resp = self.client.post(self.url, data={
            "username": "test-2",
            "password": "sample-2"
        })
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "No active account found with the given credentials")


@tag("api-tests", "auth")
class AuthLoginValidationAPITestCase(_BaseTestCase):

    def test_username_empty(self):
        self.data["username"] = ""
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["username"][0]), "This field may not be blank.")

    def test_username_exclude(self):
        self.data.pop("username")
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["username"][0]), "This field is required.")

    def test_username_null(self):
        self.data["username"] = None
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["username"][0]), "This field may not be null.")

    def test_password_empty(self):
        self.data["password"] = ""
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["password"][0]), "This field may not be blank.")

    def test_password_exclude(self):
        self.data.pop("password")
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["password"][0]), "This field is required.")

    def test_password_null(self):
        self.data["password"] = None
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["password"][0]), "This field may not be null.")

    def test_password_invalid(self):
        self.data["password"] = "invalid-password"
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "No active account found with the given credentials")
