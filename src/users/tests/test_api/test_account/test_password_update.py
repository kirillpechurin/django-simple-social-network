from django.test import tag
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
            password=cls.test_password,
            first_name="John",
            last_name="Doe",
            personal_website_url="https://example.com",
            address="sample address"
        )

    def setUp(self) -> None:
        super().setUp()

        self.client.force_authenticate(user=self.user, token=str(RefreshToken.for_user(self.user).access_token))

        self.url = "/api/v1/account/password"
        self.data = {
            "old_password": self.test_password,
            "password": "new-test-passworD1!",
            "password2": "new-test-passworD1!",
        }


@tag("api-tests", "account", "password")
class AccountUpdatePasswordAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200, resp.data)

    def test_response_data(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.data, None)

    def test_entity(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

        self.user.refresh_from_db()

        self.assertEqual(self.user.check_password(self.test_password), False)
        self.assertEqual(self.user.check_password(self.data["password"]), True)

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")


@tag("api-tests", "account")
class AccountUpdatePasswordValidationAPITestCase(_BaseTestCase):

    def test_old_password_empty(self):
        self.data["old_password"] = ""
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["old_password"][0]), "This field may not be blank.")

    def test_old_password_exclude(self):
        self.data.pop("old_password")
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["old_password"][0]), "This field is required.")

    def test_old_password_null(self):
        self.data["old_password"] = None
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["old_password"][0]), "This field may not be null.")

    def test_old_password_invalid(self):
        self.data["old_password"] = "invalid-old-password"
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["old_password"][0]), "Current password invalid.")

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
