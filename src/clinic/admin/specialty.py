from django.contrib import admin

from clinic.forms import SpecialtyAdminForm
from clinic.models import Specialty


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    """Configuração do admin para especialidades."""

    form = SpecialtyAdminForm
    list_display = ("display_name",)
    search_fields = ("name",)

    @admin.display(description="nome")
    def display_name(self, obj):
        """Exibe o nome da especialidade formatado para leitura."""
        return str(obj)
