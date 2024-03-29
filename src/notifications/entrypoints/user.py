from notifications.senders import EmailSender


class UserEntrypoint:

    def accept(self, action: str, **kwargs):
        if action == "USER_CONFIRM_EMAIL":
            return self._user_confirm_email(**kwargs)
        elif action == "USER_FORGOT_PASSWORD":
            return self._user_forgot_password(**kwargs)
        else:
            raise NotImplementedError

    def _user_confirm_email(self, data: dict):
        EmailSender(
            subject="Complete the account registration.",
            message="Confirm email and complete the account registration via the link:\n\n"
                    f"{data['link']}",
            recipient_list=[data["email"]]
        ).send()

    def _user_forgot_password(self, data: dict):
        EmailSender(
            subject="Password reset.",
            message="Complete password reset via the link:\n\n"
                    f"{data['link']}",
            recipient_list=[data["email"]]
        ).send()
