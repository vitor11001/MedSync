from decimal import Decimal, InvalidOperation

from django import forms

from clinic.models import DoctorPaymentSplitRule


class DoctorPaymentSplitRuleAdminForm(forms.ModelForm):
    """Formulário do admin para regras de repasse."""

    doctor_percentage = forms.CharField(
        label="Percentual do médico",
        help_text="Informe apenas numeros. A virgula dos decimais e o % serao aplicados automaticamente.",
        widget=forms.TextInput(
            attrs={
                "inputmode": "numeric",
                "placeholder": "0,00%",
                "maxlength": "7",
            }
        ),
    )
    clinic_percentage = forms.CharField(
        label="Percentual da clínica",
        help_text="Informe apenas numeros. A virgula dos decimais e o % serao aplicados automaticamente.",
        widget=forms.TextInput(
            attrs={
                "inputmode": "numeric",
                "placeholder": "0,00%",
                "maxlength": "7",
            }
        ),
    )

    class Meta:
        model = DoctorPaymentSplitRule
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        """Define o formato inicial de exibição dos percentuais."""
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.initial["doctor_percentage"] = self._format_percentage(
                self.instance.doctor_percentage
            )
            self.initial["clinic_percentage"] = self._format_percentage(
                self.instance.clinic_percentage
            )

    def clean_doctor_percentage(self) -> Decimal:
        """Converte o percentual do médico para decimal antes de salvar."""
        return self._clean_percentage_field("doctor_percentage")

    def clean_clinic_percentage(self) -> Decimal:
        """Converte o percentual da clínica para decimal antes de salvar."""
        return self._clean_percentage_field("clinic_percentage")

    def _clean_percentage_field(self, field_name: str) -> Decimal:
        """Normaliza o valor mascarado para um decimal válido."""
        value = self.cleaned_data.get(field_name, "")
        digits = "".join(character for character in value if character.isdigit())

        if not digits:
            raise forms.ValidationError("Informe um percentual valido.")

        normalized_value = Decimal(digits) / Decimal("100")

        if normalized_value < 0:
            raise forms.ValidationError("Informe um percentual valido.")

        if normalized_value > Decimal("100"):
            raise forms.ValidationError("O percentual nao pode ser maior que 100%.")

        try:
            return normalized_value.quantize(Decimal("0.01"))
        except InvalidOperation as exc:
            raise forms.ValidationError("Informe um percentual valido.") from exc

    @staticmethod
    def _format_percentage(value: Decimal | None) -> str:
        """Formata o decimal com vírgula e símbolo de percentual."""
        if value is None:
            return ""

        normalized = f"{value:.2f}".replace(".", ",")
        return f"{normalized}%"
