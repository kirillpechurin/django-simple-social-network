from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Extended user model.
    """

    email = models.EmailField(
        verbose_name="email address",
        unique=True
    )

    is_email_confirmed = models.BooleanField(
        verbose_name="email is verified",
        default=False
    )

    address = models.TextField(
        verbose_name="address",
        null=True,
    )

    personal_website_url = models.URLField(
        verbose_name="URL of the personal website",
        null=True,
    )
