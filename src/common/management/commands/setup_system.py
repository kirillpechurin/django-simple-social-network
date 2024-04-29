from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = "Setup system"

    def handle(self, *args, **options):
        self._load_fixtures()

    def _load_fixtures(self):
        call_command(
            "loaddata",
            *[
                "notifications/fixtures/notificationevent.json",
                "notifications/fixtures/systemnotificationtype.json",
            ]
        )
