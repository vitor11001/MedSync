from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from config.settings import get_default_superuser_settings


class Command(BaseCommand):
    """Ensures a default superuser exists when the database has none."""

    help = "Create a default superuser if there is no superuser yet."

    def handle(self, *args, **options):
        """Create the default superuser only when necessary."""
        user_model = get_user_model()
        default_superuser_settings = get_default_superuser_settings()

        if user_model.objects.filter(is_superuser=True).exists():
            self.stdout.write("A superuser already exists. Skipping creation.")
            return

        user_model.objects.create_superuser(
            email=default_superuser_settings.django_superuser_email,
            password=default_superuser_settings.django_superuser_password,
            first_name=default_superuser_settings.django_superuser_first_name,
            last_name=default_superuser_settings.django_superuser_last_name,
        )

        self.stdout.write(
            "Default superuser created: "
            f"{default_superuser_settings.django_superuser_email}"
        )
