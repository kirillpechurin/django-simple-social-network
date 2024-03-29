from django.test import tag
from rest_framework.test import APITestCase

from common.tests.mixins import MockTestCaseMixin
from users.models import User


class _BaseTestCase(APITestCase,
                    MockTestCaseMixin):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self) -> None:
        super().setUp()

        self.test_password = "test-password"
        self.user = User.objects.create_user(
            username="test",
            email="example@gmail.com",
            password=self.test_password
        )

        self.client = self.client_class()

        self.url = "/api/v1/auth/resend-confirm-email"
        self.data = {
            "email": self.user.email,
        }

        self.process_request_confirm_email_mock = self._mock(
            "users.services.auth.AuthService.request_confirm_email"
        )


@tag("api-tests", "auth")
class AuthResendConfirmEmailAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

    def test_response_data(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.data, None)

    def test_mock(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

        self.process_request_confirm_email_mock.assert_called_once()

    def test_no_user(self):
        self.data["email"] = "not-exists-user@gmail.com"
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["email"][0], "User not found.")

        self.process_request_confirm_email_mock.assert_not_called()

    def test_already_confirmed(self):
        self.user.is_email_confirmed = True
        self.user.save(update_fields=["is_email_confirmed"])

        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.data["detail"], "Already confirmed.")


@tag("api-tests", "auth")
class AuthResendConfirmEmailValidationAPITestCase(_BaseTestCase):

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
