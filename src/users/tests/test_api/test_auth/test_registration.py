from django.test import tag
from rest_framework.test import APITestCase

from users.models import User


class _BaseTestCase(APITestCase):

    def setUp(self) -> None:
        super().setUp()

        self.client = self.client_class()

        self.url = "/api/v1/auth/registration"
        self.data = {
            "username": "test",
            "password": "passworD123!",
            "password2": "passworD123!",
            "first_name": "John",
            "last_name": "Doe"
        }


@tag("api-tests", "auth")
class AuthRegistrationAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 201)

    def test_response_data(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.data, None)

    def test_entity(self):
        resp = self.client.post(self.url, data=self.data)
        user = User.objects.get()

        self.assertEqual(user.username, self.data["username"])
        self.assertEqual(user.first_name, self.data["first_name"])
        self.assertEqual(user.last_name, self.data["last_name"])
        self.assertEqual(user.check_password(self.data["password"]), True)
        self.assertEqual(user.email, "")
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_superuser, False)
        self.assertEqual(user.is_active, True)
        self.assertIsNotNone(user.date_joined)
        self.assertEqual(user.personal_website_url, None)
        self.assertEqual(user.address, None)

    def test_can_login(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 201)

        resp = self.client.post("/api/v1/auth/login", data={
            "username": self.data["username"],
            "password": self.data["password"]
        })
        self.assertEqual(resp.status_code, 200, resp.data)

    def test_username_already_exists(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 201)

        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["username"][0]), "Username already exists.")


@tag("api-tests", "auth")
class AuthRegistrationValidationAPITestCase(_BaseTestCase):

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

    def test_first_name_empty(self):
        self.data["first_name"] = ""
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["first_name"][0]), "This field may not be blank.")

    def test_first_name_exclude(self):
        self.data.pop("first_name")
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["first_name"][0]), "This field is required.")

    def test_first_name_null(self):
        self.data["first_name"] = None
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["first_name"][0]), "This field may not be null.")

    def test_last_name_empty(self):
        self.data["last_name"] = ""
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["last_name"][0]), "This field may not be blank.")

    def test_last_name_exclude(self):
        self.data.pop("last_name")
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["last_name"][0]), "This field is required.")

    def test_last_name_null(self):
        self.data["last_name"] = None
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["last_name"][0]), "This field may not be null.")
