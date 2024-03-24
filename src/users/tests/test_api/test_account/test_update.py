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
        self.data = {
            "first_name": "New John",
            "last_name": "New doe",
            "email": "new-example@gmail.com",
            "personal_website_url": "https://new-example.com",
            "address": "new sample address"
        }


@tag("api-tests", "account")
class AccountUpdateAPITestCase(_BaseTestCase):

    def test_status_code(self):
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

    def test_response_data(self):
        resp = self.client.put(self.url, data=self.data)
        self.assertIsInstance(resp.data, dict)

        self.user.refresh_from_db()

        data: dict = resp.data
        self.assertEqual(data.pop("id"), self.user.id)
        self.assertEqual(data.pop("first_name"), self.user.first_name)
        self.assertEqual(data.pop("last_name"), self.user.last_name)
        self.assertEqual(data.pop("username"), self.user.username)
        self.assertEqual(data.pop("email"), self.user.email)
        self.assertEqual(data.pop("personal_website_url"), self.user.personal_website_url)
        self.assertEqual(data.pop("address"), self.user.address)

        self.assertEqual(data, {})

    def test_entity(self):
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, self.data["first_name"])
        self.assertEqual(self.user.last_name, self.data["last_name"])
        self.assertEqual(self.user.username, "test")
        self.assertEqual(self.user.email, self.data["email"])
        self.assertEqual(self.user.personal_website_url, self.data["personal_website_url"])
        self.assertEqual(self.user.address, self.data["address"])
        self.assertEqual(self.user.check_password("test-password"), True)

    def test_not_authenticated(self):
        self.client = self.client_class()
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(str(resp.data["detail"]), "Authentication credentials were not provided.")


@tag("api-tests", "account")
class AccountUpdateValidationAPITestCase(_BaseTestCase):

    def test_first_name_empty(self):
        self.data["first_name"] = ""
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["first_name"][0]), "This field may not be blank.")

    def test_first_name_exclude(self):
        self.data.pop("first_name")
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["first_name"][0]), "This field is required.")

    def test_first_name_null(self):
        self.data["first_name"] = None
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["first_name"][0]), "This field may not be null.")

    def test_last_name_empty(self):
        self.data["last_name"] = ""
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["last_name"][0]), "This field may not be blank.")

    def test_last_name_exclude(self):
        self.data.pop("last_name")
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["last_name"][0]), "This field is required.")

    def test_last_name_null(self):
        self.data["last_name"] = None
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["last_name"][0]), "This field may not be null.")

    def test_email_empty(self):
        self.data["email"] = ""
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

    def test_email_exclude(self):
        self.data.pop("email")
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["email"][0]), "This field is required.")

    def test_email_null(self):
        self.data["email"] = None
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["email"][0]), "This field may not be null.")

    def test_email_invalid(self):
        self.data["email"] = "invalid"
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["email"][0]), "Enter a valid email address.")

    def test_personal_website_url_empty(self):
        self.data["personal_website_url"] = ""
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["personal_website_url"][0]), "This field may not be blank.")

    def test_personal_website_url_exclude(self):
        self.data.pop("personal_website_url")
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["personal_website_url"][0]), "This field is required.")

    def test_personal_website_url_null(self):
        self.data["personal_website_url"] = None
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

    def test_personal_website_url_invalid(self):
        self.data["personal_website_url"] = "invalid"
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["personal_website_url"][0]), "Enter a valid URL.")

    def test_address_empty(self):
        self.data["address"] = ""
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["address"][0]), "This field may not be blank.")

    def test_address_exclude(self):
        self.data.pop("address")
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(str(resp.data["address"][0]), "This field is required.")

    def test_address_null(self):
        self.data["address"] = None
        resp = self.client.put(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)
