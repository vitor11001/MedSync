from django.contrib import admin

from clinic.models import Phone


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    """Configuracao do admin para telefones."""

    list_display = ("number", "is_deleted")
    search_fields = ("number",)
    list_filter = ("is_deleted", "created_at")
