from django.apps import AppConfig


class ClinicConfig(AppConfig):
    """Application configuration for clinic domain logic."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "clinic"
    verbose_name = "Clinica"
