import re

from django import forms
from django.contrib import admin

from clinic.models import Doctor


class DoctorAdminForm(forms.ModelForm):
    """Formulário do admin para médicos."""

    crm = forms.CharField(label="CRM")

    class Meta:
        model = Doctor
        exclude = ("is_deleted", "deleted_at")
        widgets = {
            "phone_primary": forms.TextInput(
                attrs={
                    "maxlength": "15",
                    "inputmode": "numeric",
                    "pattern": "[0-9]*",
                    "placeholder": "(81) 99999-9999",
                }
            ),
            "phone_secondary": forms.TextInput(
                attrs={
                    "maxlength": "15",
                    "inputmode": "numeric",
                    "pattern": "[0-9]*",
                    "placeholder": "(81) 99999-9999",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "email@exemplo.com",
                }
            ),
        }

    def clean_phone_primary(self) -> str:
        """Valida e formata o telefone principal."""
        return self._clean_phone_field("phone_primary")

    def clean_phone_secondary(self) -> str:
        """Valida e formata o telefone secundario."""
        return self._clean_phone_field("phone_secondary")

    def _clean_phone_field(self, field_name: str) -> str:
        """Aplica validacao e mascara ao telefone informado."""
        value = self.cleaned_data.get(field_name, "")

        if not value:
            return ""

        digits = re.sub(r"\D", "", value)

        if len(digits) != 11:
            raise forms.ValidationError(
                "O telefone deve ter exatamente 11 numeros, no formato DDD + numero."
            )

        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"


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
        js = ("clinic/admin/client_form.js",)
