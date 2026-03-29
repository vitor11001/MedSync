from django.contrib import admin

from clinic.forms import DoctorAdminForm
from clinic.models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """Configuração do admin para médicos."""

    form = DoctorAdminForm
    filter_horizontal = ("specialties",)
    list_display = (
        "display_full_name",
        "specialties_list",
        "crm",
        "phone_primary",
        "email",
        "is_active",
    )
    search_fields = ("full_name", "crm")

    @admin.display(description="nome completo")
    def display_full_name(self, obj):
        """Exibe o nome do médico formatado para leitura."""
        return obj.full_name.title()

    @admin.display(description="especialidades")
    def specialties_list(self, obj):
        """Exibe as especialidades vinculadas ao médico."""
        return obj.specialties_display()

    class Media:
        js = (
            "clinic/vendor/jquery.min.js",
            "clinic/vendor/jquery.mask.min.js",
            "clinic/admin/client_form.js",
        )
