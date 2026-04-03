from decimal import Decimal, InvalidOperation

from django import forms

from clinic.models import Appointment


class AppointmentAdminForm(forms.ModelForm):
    """Formulário do admin para consultas."""

    total_amount = forms.CharField(
        label="valor total (R$)",
        help_text="Informe o valor total da consulta. A soma dos pagamentos deve bater com este valor.",
        widget=forms.TextInput(
            attrs={
                "inputmode": "numeric",
                "placeholder": "0,00",
                "maxlength": "13",
                "class": "js-money-mask",
            }
        ),
    )

    class Meta:
        model = Appointment
        exclude = ("is_deleted", "deleted_at")

    def __init__(self, *args, **kwargs):
        """Define valores iniciais e formato de exibição no admin."""
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.fields["consultation_type"].initial = (
                Appointment.ConsultationType.FIRST_CONSULTATION
            )

        if self.instance.pk and self.instance.total_amount is not None:
            self.initial["total_amount"] = self._format_amount(self.instance.total_amount)

    def clean_total_amount(self) -> Decimal:
        """Converte o valor formatado em decimal para persistência."""
        value = self.cleaned_data.get("total_amount", "")
        digits = "".join(character for character in value if character.isdigit())

        if not digits:
            raise forms.ValidationError("Informe o valor total da consulta.")

        normalized_value = Decimal(digits) / Decimal("100")

        if normalized_value <= 0:
            raise forms.ValidationError("Informe um valor maior que zero.")

        try:
            return normalized_value.quantize(Decimal("0.01"))
        except InvalidOperation as exc:
            raise forms.ValidationError("Informe um valor valido.") from exc

    @staticmethod
    def _format_amount(value: Decimal) -> str:
        """Formata o valor decimal com vírgula para exibição no formulário."""
        normalized = f"{value:.2f}"
        integer_part, decimal_part = normalized.split(".")
        return f"{integer_part},{decimal_part}"
