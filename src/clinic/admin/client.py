from django.contrib import admin

from clinic.forms import ClientAdminForm
from clinic.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Configuração do admin para pacientes."""

    form = ClientAdminForm
    list_display = (
        "display_full_name",
        "birth_date",
        "sex",
        "cpf",
        "phone_primary",
        "email",
    )
    search_fields = ("full_name", "cpf")

    @admin.display(description="nome completo")
    def display_full_name(self, obj):
        """Exibe o nome do paciente formatado para leitura."""
        return obj.full_name.title()

    class Media:
        js = (
            "clinic/vendor/jquery.min.js",
            "clinic/vendor/jquery.mask.min.js",
            "clinic/admin/client_form.js",
        )
