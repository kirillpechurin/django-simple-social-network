from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int


class TokenGenerator(PasswordResetTokenGenerator):

    def check_token(self, entity, token):
        if not (entity and token):
            return False
        # Parse the token
        try:
            ts_b36, _ = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        for secret in [self.secret, *self.secret_fallbacks]:
            if constant_time_compare(
                    self._make_token_with_timestamp(
                        entity,
                        ts,
                        secret
                    ),
                    token,
            ):
                break
        else:
            return False

        # Check the timestamp is within limit.
        if (self._num_seconds(self._now()) - ts) > self._get_timeout():
            return self._process_expired()

        return True

    def _get_timeout(self):
        # Can use for `mock` in auto tests.
        raise NotImplementedError

    def _process_expired(self):
        return False

    def _make_hash_value(self, entity, timestamp):
        raise NotImplementedError
