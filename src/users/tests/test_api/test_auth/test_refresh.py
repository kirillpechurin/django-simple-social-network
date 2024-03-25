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

        self.url = "/api/v1/auth/refresh"
        self.data = {
            "refresh": str(self.refresh_token),
        }


@tag("api-tests", "auth")
class AuthRefreshAPITestCase(_BaseTestCase):

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
        self.data["refresh"] = str(RefreshToken.for_user(user))
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

    def test_cannot_use_again(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Token is blacklisted")


@tag("api-tests", "auth")
class AuthRefreshValidationAPITestCase(_BaseTestCase):

    def test_refresh_empty(self):
        self.data["refresh"] = ""
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["refresh"][0]), "This field may not be blank.")

    def test_refresh_exclude(self):
        self.data.pop("refresh")
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["refresh"][0]), "This field is required.")

    def test_refresh_null(self):
        self.data["refresh"] = None
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["refresh"][0]), "This field may not be null.")

    def test_refresh_invalid(self):
        self.data["refresh"] = "invalid"
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Token is invalid or expired")
