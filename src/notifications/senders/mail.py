from typing import List

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


class EmailSenderInterface:

    def send(self):
        raise NotImplementedError


class AbstractEmailSender(EmailSenderInterface):

    def __init__(self,
                 subject: str,
                 message: str,
                 recipient_list: List[str]):
        self._subject = subject
        self._message = message
        self._recipient_list = recipient_list

    def _send(self, msg):
        status = msg.send()
        return bool(status)

    def _get_msg(self, **kwargs):
        return EmailMultiAlternatives(
            subject=self._subject,
            body=self._message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=self._recipient_list,
            **kwargs
        )

    def send(self):
        msg = self._get_msg()
        return self._send(msg)


class EmailSender(AbstractEmailSender):
    pass
