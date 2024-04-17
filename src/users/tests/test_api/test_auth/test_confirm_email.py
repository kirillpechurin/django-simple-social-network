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
            password=cls.test_password,
            is_email_confirmed=False
        )

    def setUp(self) -> None:
        super().setUp()

        self.client = self.client_class()

        self.url = "/api/v1/auth/confirm-email"

        uid = auth_tokens.UidGenerator().make(self.user)
        token = auth_tokens.ConfirmEmailTokenGenerator().make_token(self.user)
        self.data = {
            "uid": uid,
            "token": token,
        }


@tag("api-tests", "auth")
class AuthConfirmEmailAPITestCase(_BaseTestCase):

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
        self.assertTrue(self.user.is_email_confirmed, True)

    def test_not_is_active(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_confirmed, True)

    def test_already_confirmed(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_confirmed, True)

        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["detail"], "Already confirmed.")


@tag("api-tests", "auth")
class AuthConfirmEmailValidationAPITestCase(_BaseTestCase):

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
        self.data["token"] = auth_tokens.ConfirmEmailTokenGenerator().make_token(user)
        resp = self.client.post(self.url, data=self.data)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["detail"], "Invalid token.")
