from django.contrib import admin

from clinic.models import Email


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    """Configuracao do admin para emails."""

    list_display = ("email", "is_deleted")
    search_fields = ("email",)
    list_filter = ("is_deleted", "created_at")
