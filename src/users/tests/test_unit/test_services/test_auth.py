from urllib import parse

from django.test import TestCase, tag
from rest_framework import exceptions

from common.tests.mixins import MockTestCaseMixin
from users.models import User
from users.services.auth import AuthService
from users.tokens.auth import UidGenerator, ConfirmEmailTokenGenerator, PasswordResetTokenGenerator


@tag("unit-tests", "auth")
class AuthServiceRequestConfirmEmailTestCase(TestCase,
                                             MockTestCaseMixin):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test",
            email="example@gmail.com",
            password="test-password"
        )

        super().setUpTestData()

    def setUp(self) -> None:
        super().setUp()

        self.mock_notifications_handler = self._mock(
            "notifications.entrypoint.Handler.accept"
        )

    def _call(self, user: User):
        return AuthService.request_confirm_email(user)

    def test_notifications_handler(self):
        self._call(self.user)

        self.mock_notifications_handler.assert_called_once()

        call = self.mock_notifications_handler.mock_calls[0]
        self.assertEqual(len(call.args), 0)
        self.assertEqual(len(call.kwargs.keys()), 2)

        self.assertEqual(call.kwargs["action"], "USER_CONFIRM_EMAIL")

        data = call.kwargs["data"]
        self.assertEqual(len(data.keys()), 2)
        self.assertEqual(data["email"], self.user.email)

        payload = parse.parse_qs(parse.urlparse(data["link"]).query)
        self.assertEqual(UidGenerator().get(payload["uid"][0]), self.user.pk)
        self.assertTrue(ConfirmEmailTokenGenerator().check_token(self.user, payload["token"][0]))


@tag("unit-tests", "auth")
class AuthServiceResendRequestConfirmEmailTestCase(TestCase,
                                                   MockTestCaseMixin):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test",
            email="example@gmail.com",
            password="test-password"
        )

        super().setUpTestData()

    def setUp(self) -> None:
        super().setUp()

        self.mock_request = self._mock(
            "users.services.auth.AuthService.request_confirm_email"
        )

    def _call(self, user: User):
        return AuthService.resend_request_confirm_email(user)

    def test_default(self):
        self._call(self.user)

        self.mock_request.assert_called_once()

    def test_is_confirmed(self):
        self.user.is_email_confirmed = True
        self.user.save(update_fields=["is_email_confirmed"])
        try:
            self._call(self.user)
        except Exception as ex:
            self.assertIsInstance(ex, exceptions.APIException)
            self.assertEqual(str(ex.detail), "Already confirmed.")
            self.assertEqual(ex.detail.code, "already_confirmed")
        else:
            self.assertFalse(True)


@tag("unit-tests", "auth")
class AuthServiceConfirmEmailTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test",
            email="example@gmail.com",
            password="test-password"
        )

        super().setUpTestData()

    def setUp(self) -> None:
        super().setUp()
        self.data = {
            "uid": UidGenerator().make(self.user),
            "token": ConfirmEmailTokenGenerator().make_token(self.user)
        }

    def _call(self, data: dict):
        return AuthService.confirm_email(data=data)

    def test_default(self):
        self.assertEqual(self.user.is_email_confirmed, False)

        self._call(self.data)

        self.user.refresh_from_db()
        self.assertEqual(self.user.is_email_confirmed, True)

    def test_uid_invalid(self):
        self.data["uid"] = "invalid"
        try:
            self._call(self.data)
        except Exception as ex:
            self.assertIsInstance(ex, exceptions.APIException)
            self.assertEqual(str(ex.detail), "Invalid token.")
            self.assertEqual(ex.detail.code, "confirm_email_invalid_token")
        else:
            self.assertFalse(True)

    def test_uid_user_not_found(self):
        self.data["uid"] = UidGenerator().make(User(id=999))
        try:
            self._call(self.data)
        except Exception as ex:
            self.assertIsInstance(ex, exceptions.APIException)
            self.assertEqual(str(ex.detail), "Invalid token.")
            self.assertEqual(ex.detail.code, "confirm_email_invalid_token")
        else:
            self.assertFalse(True)

    def test_token_invalid(self):
        self.data["token"] = "invalid"
        try:
            self._call(self.data)
        except Exception as ex:
            self.assertIsInstance(ex, exceptions.APIException)
            self.assertEqual(str(ex.detail), "Invalid token.")
            self.assertEqual(ex.detail.code, "confirm_email_invalid_token")
        else:
            self.assertFalse(True)

    def test_is_confirmed(self):
        self.user.is_email_confirmed = True
        self.user.save(update_fields=["is_email_confirmed"])
        try:
            self._call(self.data)
        except Exception as ex:
            self.assertIsInstance(ex, exceptions.APIException)
            self.assertEqual(str(ex.detail), "Already confirmed.")
            self.assertEqual(ex.detail.code, "already_confirmed")
        else:
            self.assertFalse(True)


@tag("unit-tests", "auth")
class AuthServiceProcessForgotPasswordTestCase(TestCase,
                                               MockTestCaseMixin):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test",
            email="example@gmail.com",
            password="test-password",
            is_email_confirmed=True
        )

        super().setUpTestData()

    def setUp(self) -> None:
        super().setUp()

        self.mock_notifications_handler = self._mock(
            "notifications.entrypoint.Handler.accept"
        )

        self.data = {
            "email": self.user.email
        }

    def _call(self, data: dict):
        return AuthService.process_forgot_password(data)

    def test_mock(self):
        self._call(self.data)

        self.mock_notifications_handler.assert_called_once()

        call = self.mock_notifications_handler.mock_calls[0]
        self.assertEqual(len(call.args), 0)
        self.assertEqual(len(call.kwargs.keys()), 2)

        self.assertEqual(call.kwargs["action"], "USER_FORGOT_PASSWORD")

        data = call.kwargs["data"]
        self.assertEqual(len(data.keys()), 2)
        self.assertEqual(data["email"], self.user.email)

        payload = parse.parse_qs(parse.urlparse(data["link"]).query)
        self.assertEqual(UidGenerator().get(payload["uid"][0]), self.user.pk)
        self.assertTrue(PasswordResetTokenGenerator().check_token(self.user, payload["token"][0]))

    def test_not_exist_user(self):
        self._call(data={"email": "not-exists@gmail.com"})

        self.mock_notifications_handler.assert_not_called()

    def test_not_is_email_confirmed(self):
        self.user.is_email_confirmed = False
        self.user.save(update_fields=["is_email_confirmed"])
        try:
            self._call(self.data)
        except Exception as ex:
            self.assertIsInstance(ex, exceptions.APIException)
            self.assertEqual(str(ex.detail), "Email not confirmed.")
            self.assertEqual(ex.detail.code, "email_not_confirmed")
        else:
            self.assertFalse(True)

    def test_not_is_active(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        try:
            self._call(self.data)
        except Exception as ex:
            self.assertIsInstance(ex, exceptions.APIException)
            self.assertEqual(str(ex.detail), "User is not active.")
            self.assertEqual(ex.detail.code, "user_is_not_active")
        else:
            self.assertFalse(True)


@tag("unit-tests", "auth")
class AuthServiceProcessResetPasswordTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test",
            email="example@gmail.com",
            password="test-password"
        )

        super().setUpTestData()

    def setUp(self) -> None:
        super().setUp()
        self.data = {
            "uid": UidGenerator().make(self.user),
            "token": PasswordResetTokenGenerator().make_token(self.user),
            "password": "new-password123!"
        }

    def _call(self, data: dict):
        return AuthService.process_reset_password(data=data)

    def test_default(self):
        self.assertFalse(self.user.check_password(self.data["password"]))

        self._call(self.data)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.data["password"]))

    def test_uid_invalid(self):
        self.data["uid"] = "invalid"
        try:
            self._call(self.data)
        except Exception as ex:
            self.assertIsInstance(ex, exceptions.APIException)
            self.assertEqual(str(ex.detail), "Invalid token.")
            self.assertEqual(ex.detail.code, "reset_password_invalid_token")
        else:
            self.assertFalse(True)

    def test_uid_user_not_found(self):
        self.data["uid"] = UidGenerator().make(User(id=999))
        try:
            self._call(self.data)
        except Exception as ex:
            self.assertIsInstance(ex, exceptions.APIException)
            self.assertEqual(str(ex.detail), "Invalid token.")
            self.assertEqual(ex.detail.code, "reset_password_invalid_token")
        else:
            self.assertFalse(True)

    def test_token_invalid(self):
        self.data["token"] = "invalid"
        try:
            self._call(self.data)
        except Exception as ex:
            self.assertIsInstance(ex, exceptions.APIException)
            self.assertEqual(str(ex.detail), "Invalid token.")
            self.assertEqual(ex.detail.code, "reset_password_invalid_token")
        else:
            self.assertFalse(True)
