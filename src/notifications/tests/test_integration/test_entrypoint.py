from unittest.mock import patch

from django.test import TestCase

from notifications import Handler


class NotificationsEntrypointIntegrationTestCase(TestCase):

    def _call(self,
              action: str,
              **kwargs):
        Handler.accept(action, **kwargs)

    def test_user_confirm_email(self):
        with patch("notifications.entrypoints.user.UserEntrypoint.accept") as mock:
            self._call(
                action="USER_CONFIRM_EMAIL",
                data={
                    "link": "sample-link",
                    "email": "sample@gmail.com"
                }
            )
            mock.assert_called_once_with(
                "USER_CONFIRM_EMAIL",
                data={
                    "link": "sample-link",
                    "email": "sample@gmail.com"
                }
            )

    def test_user_forgot_password(self):
        with patch("notifications.entrypoints.user.UserEntrypoint.accept") as mock:
            self._call(
                action="USER_CONFIRM_EMAIL",
                data={
                    "link": "sample-link",
                    "email": "sample@gmail.com"
                }
            )
            mock.assert_called_once_with(
                "USER_CONFIRM_EMAIL",
                data={
                    "link": "sample-link",
                    "email": "sample@gmail.com"
                }
            )

    def test_unknown_action(self):
        self.assertRaises(NotImplementedError, self._call, action="UNKNOWN_ACTION", data={})
