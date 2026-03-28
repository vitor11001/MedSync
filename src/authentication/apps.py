from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """Application configuration for authentication."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"
    verbose_name = "Usuarios e Acessos"
