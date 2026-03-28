from django.contrib import admin

from clinic.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Configuracao do admin para pacientes."""

    list_display = ("full_name", "birth_date", "sex", "cpf", "is_deleted")
    search_fields = ("full_name", "cpf")
    list_filter = ("sex", "is_deleted", "created_at")
    filter_horizontal = ("phones", "emails")
