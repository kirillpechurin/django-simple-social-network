from django.conf import settings
from django.core import mail
from django.test import TestCase

from notifications.entrypoints import UserEntrypoint


class NotificationsUserEntrypointIntegrationTestCase(TestCase):

    def _call(self,
              action: str,
              **kwargs):
        UserEntrypoint().accept(action, **kwargs)

    def test_user_confirm_email(self):
        self._call(
            action="USER_CONFIRM_EMAIL",
            data={
                "link": "sample-link",
                "email": "sample@gmail.com"
            }
        )

        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual(mail.outbox[0].subject, "Complete the account registration.")
        self.assertEqual(
            mail.outbox[0].body,
            "Confirm email and complete the account registration via the link:\n\n"
            "sample-link"
        )
        self.assertEqual(mail.outbox[0].recipients(), ["sample@gmail.com"])
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

    def test_user_forgot_password(self):
        self._call(
            action="USER_FORGOT_PASSWORD",
            data={
                "link": "sample-link",
                "email": "sample@gmail.com"
            }
        )

        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual(mail.outbox[0].subject, "Password reset.")
        self.assertEqual(
            mail.outbox[0].body,
            "Complete password reset via the link:\n\n"
            "sample-link"
        )
        self.assertEqual(mail.outbox[0].recipients(), ["sample@gmail.com"])
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)

    def test_unknown_action(self):
        self.assertRaises(NotImplementedError, self._call, action="UNKNOWN_ACTION", data={})
