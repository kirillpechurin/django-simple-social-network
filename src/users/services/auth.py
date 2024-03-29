from django.conf import settings
from rest_framework import exceptions

from common import exceptions as custom_exceptions
from notifications import Handler as NotificationsHandler
from users.models import User
from users.tokens import auth as auth_tokens


class AuthService:

    @staticmethod
    def request_confirm_email(user: User):
        uid = auth_tokens.UidGenerator().make(user)
        token = auth_tokens.ConfirmEmailTokenGenerator().make_token(user)

        NotificationsHandler.accept(
            action="USER_CONFIRM_EMAIL",
            data={
                "link": f"{settings.PUBLIC_HOST}/confirm-email?uid={uid}&token={token}",
                "email": user.email
            }
        )
        return user

    @staticmethod
    def resend_request_confirm_email(user: User):
        if user.is_email_confirmed:
            raise exceptions.PermissionDenied("Already confirmed.", code="already_confirmed")

        return AuthService.request_confirm_email(user)

    @staticmethod
    def confirm_email(data: dict):
        uid = auth_tokens.UidGenerator().get(data["uid"])

        user = User.objects.filter(id=uid).first()
        if not user:
            raise custom_exceptions.BadRequest("Invalid token.", code="confirm_email_invalid_token")

        if not auth_tokens.ConfirmEmailTokenGenerator().check_token(user, data["token"]):
            raise custom_exceptions.BadRequest("Invalid token.", code="confirm_email_invalid_token")

        if user.is_email_confirmed:
            raise custom_exceptions.BadRequest("Already confirmed.", code="already_confirmed")

        user.is_email_confirmed = True
        user.save(update_fields=["is_email_confirmed"])

        return user

    @staticmethod
    def process_forgot_password(data: dict):
        user = User.objects.filter(email=data["email"]).first()
        if not user:
            return

        if not user.is_active:
            raise custom_exceptions.BadRequest("User is not active.", code="user_is_not_active")

        if not user.is_email_confirmed:
            raise custom_exceptions.BadRequest("Email not confirmed.", code="email_not_confirmed")

        uid = auth_tokens.UidGenerator().make(user)
        token = auth_tokens.PasswordResetTokenGenerator().make_token(user)

        NotificationsHandler.accept(
            action="USER_FORGOT_PASSWORD",
            data={
                "link": f"{settings.PUBLIC_HOST}/forgot-password?uid={uid}&token={token}",
                "email": user.email
            }
        )
        return user

    @staticmethod
    def process_reset_password(data: dict):
        uid = auth_tokens.UidGenerator().get(data["uid"])

        user = User.objects.filter(id=uid).first()
        if not user:
            raise custom_exceptions.BadRequest("Invalid token.", code="reset_password_invalid_token")

        if not auth_tokens.PasswordResetTokenGenerator().check_token(user, data["token"]):
            raise custom_exceptions.BadRequest("Invalid token.", code="reset_password_invalid_token")

        user.set_password(data["password"])
        user.save(update_fields=["password"])
        return user
