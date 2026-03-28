from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

from authentication.models import AuthenticationGroup


try:
    admin.site.unregister(Group)
except NotRegistered:
    pass


@admin.register(AuthenticationGroup)
class AuthenticationGroupAdmin(GroupAdmin):
    """Configuracao do admin para grupos de usuarios."""
