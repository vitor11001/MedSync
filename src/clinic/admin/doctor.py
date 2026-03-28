from django.contrib import admin

from clinic.models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """Configuracao do admin para medicos."""

    list_display = ("full_name", "specialty", "crm", "is_active", "is_deleted")
    search_fields = ("full_name", "specialty", "crm")
    list_filter = ("is_active", "is_deleted", "created_at")
    filter_horizontal = ("phones", "emails")
