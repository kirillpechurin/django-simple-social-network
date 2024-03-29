from django.test import tag
from rest_framework.test import APITestCase

from common.tests.mixins import MockTestCaseMixin
from users.models import User


class _BaseTestCase(APITestCase,
                    MockTestCaseMixin):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.test_password = "test-password"
        cls.user = User.objects.create_user(
            username="test",
            email="example@gmail.com",
            password=cls.test_password,
            is_email_confirmed=True
        )

    def setUp(self) -> None:
        super().setUp()

        self.client = self.client_class()

        self.url = "/api/v1/auth/forgot-password"
        self.data = {
            "email": self.user.email,
        }

        self.notification_forgot_password_mock = self._mock(
            "notifications.entrypoint.Handler.accept"
        )


@tag("api-tests", "auth")
class AuthForgotPasswordAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200, resp.data)

    def test_response_data(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.data, None)

    def test_mock(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

        self.notification_forgot_password_mock.assert_called_once()

    def test_no_user(self):
        self.data["email"] = "not-exists-user@gmail.com"
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

        self.notification_forgot_password_mock.assert_not_called()

    def test_not_is_email_confirmed(self):
        user = User.objects.create_user("not-confirmed", "not-confirmed-email@gmail.com", "test-123")
        self.data["email"] = user.email

        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["detail"], "Email not confirmed.")

    def test_not_is_active(self):
        user = User.objects.create_user("not-confirmed", "not-confirmed-email@gmail.com", "test-123", is_active=False)
        self.data["email"] = user.email

        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["detail"]), "User is not active.")


@tag("api-tests", "auth")
class AuthForgotPasswordValidationAPITestCase(_BaseTestCase):

    def test_email_empty(self):
        self.data["email"] = ""
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["email"][0]), "This field may not be blank.")

    def test_email_exclude(self):
        self.data.pop("email")
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["email"][0]), "This field is required.")

    def test_email_null(self):
        self.data["email"] = None
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["email"][0]), "This field may not be null.")

    def test_email_invalid(self):
        self.data["email"] = "invalid"
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["email"][0]), "Enter a valid email address.")
