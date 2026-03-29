from django import forms
from django.contrib import admin

from clinic.models import Specialty


class SpecialtyAdminForm(forms.ModelForm):
    """Formulário do admin para especialidades."""

    class Meta:
        model = Specialty
        exclude = ("is_deleted", "deleted_at")


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
