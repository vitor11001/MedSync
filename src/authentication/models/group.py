from django.contrib.auth.models import Group


class AuthenticationGroup(Group):
    """Proxy do model Group para exibi-lo no app de autenticação."""

    class Meta:
        proxy = True
        app_label = "authentication"
        verbose_name = "Grupo"
        verbose_name_plural = "Grupos"
