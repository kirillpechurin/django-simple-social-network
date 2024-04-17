import os

from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand
from django.db import models

from common.utils import JsonFile


class Command(BaseCommand):
    help = "Setup handbooks"

    def handle(self, *args, **options):
        for content_type in ContentType.objects.order_by("app_label", "id"):
            content_type: ContentType
            model: models.Model = content_type.model_class()
            if hasattr(model, "Handbook") and isinstance(model.Handbook, models.enums.ChoicesType):
                data = [
                    {
                        "model": f"{content_type.app_label}.{content_type.model}",
                        "pk": option.value,
                        "fields": {
                            "title": option.label
                        }
                    }
                    for option in model.Handbook
                ]
                directory = f"{content_type.app_label}/fixtures/"
                os.makedirs(directory, exist_ok=True)
                filename = f"{content_type.app_label}/fixtures/{content_type.model}.json"
                JsonFile(filename).write(data)
