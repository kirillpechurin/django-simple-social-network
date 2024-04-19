from django.test import tag
from rest_framework.test import APITestCase

from common.tests.mixins import MockTestCaseMixin
from users.models import User
from users.tokens import auth as auth_tokens


class _BaseTestCase(APITestCase,
                    MockTestCaseMixin):

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

        self.url = "/api/v1/auth/reset-password"

        uid = auth_tokens.UidGenerator().make(self.user)
        token = auth_tokens.PasswordResetTokenGenerator().make_token(self.user)
        self.data = {
            "uid": uid,
            "token": token,
            "password": "new-Password123!",
            "password2": "new-Password123!",
        }


@tag("api-tests", "auth")
class AuthResetPasswordAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

    def test_response_data(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.data, None)

    def test_entity(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.data["password"]))


@tag("api-tests", "auth")
class AuthResetPasswordValidationAPITestCase(_BaseTestCase):

    def test_uid_empty(self):
        self.data["uid"] = ""
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(str(resp.data["uid"][0]), "This field may not be blank.")

    def test_uid_exclude(self):
        self.data.pop("uid")
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(str(resp.data["uid"][0]), "This field is required.")

    def test_uid_null(self):
        self.data["uid"] = None
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(str(resp.data["uid"][0]), "This field may not be null.")

    def test_uid_invalid(self):
        self.data["uid"] = "invalid-uid"
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.data["detail"], "Invalid token.")

    def test_uid_user_not_found(self):
        self.data["uid"] = auth_tokens.UidGenerator().make(User(id=999))
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["detail"], "Invalid token.")

    def test_uid_other_user(self):
        user = User.objects.create_user("test-2", password="test-2", email="test@gmail.com")
        self.data["uid"] = auth_tokens.UidGenerator().make(user)
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["detail"], "Invalid token.")

    def test_token_empty(self):
        self.data["token"] = ""
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(str(resp.data["token"][0]), "This field may not be blank.")

    def test_token_exclude(self):
        self.data.pop("token")
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(str(resp.data["token"][0]), "This field is required.")

    def test_token_null(self):
        self.data["token"] = None
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(str(resp.data["token"][0]), "This field may not be null.")

    def test_token_invalid(self):
        self.data["token"] = "invalid"
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["detail"], "Invalid token.")

    def test_token_other_user(self):
        user = User.objects.create_user("test-2", password="test-2", email="test@gmail.com")
        self.data["token"] = auth_tokens.PasswordResetTokenGenerator().make_token(user)
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["detail"], "Invalid token.")

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

    def test_password_less_than_8(self):
        self.data["password"] = "123"
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["password"][0]), "Ensure this value has at least 8 characters.")

    def test_password_more_than_128(self):
        self.data["password"] = "1" * 200
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["password"][0]), "Ensure this value has at most 128 characters.")

    def test_password_has_not_contains_one_digit(self):
        self.data["password"] = "passwordD!"
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["password"][0]), "Ensure this value contains one digit.")

    def test_password_has_not_contains_one_capital_letter(self):
        self.data["password"] = "password!1"
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["password"][0]), "Ensure this value contains one capital letter.")

    def test_password_has_not_contains_one_special_symbol(self):
        self.data["password"] = "passwordD1"
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["password"][0]), "Ensure this value contains one special symbol.")

    def test_password2_empty(self):
        self.data["password2"] = ""
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["password2"][0]), "This field may not be blank.")

    def test_password2_exclude(self):
        self.data.pop("password2")
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["password2"][0]), "This field is required.")

    def test_password2_null(self):
        self.data["password2"] = None
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["password2"][0]), "This field may not be null.")

    def test_password2_not_equal_password(self):
        self.data["password2"] = "invalid-password"
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["password2"][0]), "Password invalid.")
