from django.conf import settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from common import tokens as custom_tokens


class UidGenerator:

    def make(self, user):
        return urlsafe_base64_encode(force_bytes(user.pk))

    def get(self, value):
        try:
            return urlsafe_base64_decode(value).decode()
        except Exception as ex:
            return None


class PasswordResetTokenGenerator(custom_tokens.TokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{user.password}{timestamp}{user.email}"

    def _get_timeout(self):
        return settings.PASSWORD_RESET_TIMEOUT


class ConfirmEmailTokenGenerator(custom_tokens.TokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{user.email}{timestamp}"

    def _get_timeout(self):
        return settings.CONFIRM_EMAIL_TIMEOUT
