import re

from django import forms
from django.forms import DateInput

from clinic.models import Client


class ClientAdminForm(forms.ModelForm):
    """Formulário do admin para pacientes."""

    birth_date = forms.DateField(
        label="Data de nascimento",
        required=True,
        input_formats=["%d/%m/%Y"],
        widget=DateInput(
            format="%d/%m/%Y",
            attrs={
                "placeholder": "dd/mm/aaaa",
            },
        ),
        help_text="Informe a data de nascimento no formato dia/mes/ano.",
        error_messages={
            "required": "Informe a data de nascimento do paciente.",
            "invalid": (
                "Informe a data de nascimento com dia, mes e ano completos "
                "no formato dd/mm/aaaa."
            ),
        },
    )

    class Meta:
        model = Client
        exclude = ("is_deleted", "deleted_at")
        widgets = {
            "cpf": forms.TextInput(
                attrs={
                    "maxlength": "14",
                    "inputmode": "numeric",
                    "placeholder": "000.000.000-00",
                }
            ),
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

    def clean_cpf(self) -> str:
        """Valida e formata o CPF."""
        cpf = self.cleaned_data.get("cpf")

        if not cpf:
            return ""

        digits = re.sub(r"\D", "", cpf)

        if len(digits) != 11:
            raise forms.ValidationError("Informe um CPF com 11 numeros.")

        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"

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

        return self._format_phone_number(digits)

    @staticmethod
    def _format_phone_number(digits: str) -> str:
        """Aplica uma mascara simples ao telefone salvo."""
        if len(digits) == 11:
            return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"

        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
