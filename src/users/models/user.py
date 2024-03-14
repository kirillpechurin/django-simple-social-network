from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Extended user model.
    """

    address = models.TextField(
        verbose_name="address",
        null=True,
    )

    personal_website_url = models.URLField(
        verbose_name="URL of the personal website",
        null=True,
    )
