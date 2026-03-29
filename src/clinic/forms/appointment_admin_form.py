from decimal import Decimal, InvalidOperation

from django import forms

from clinic.models import Appointment


class AppointmentAdminForm(forms.ModelForm):
    """Formulário do admin para consultas."""

    amount_paid = forms.CharField(
        label="valor pago (R$)",
        help_text="Informe apenas numeros. A virgula dos centavos sera aplicada automaticamente.",
        widget=forms.TextInput(
            attrs={
                "inputmode": "numeric",
                "placeholder": "0,00",
                "maxlength": "13",
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

        if self.instance.pk and self.instance.amount_paid is not None:
            self.initial["amount_paid"] = self._format_amount(self.instance.amount_paid)

    def clean_amount_paid(self) -> Decimal:
        """Converte o valor formatado em decimal para persistência."""
        value = self.cleaned_data.get("amount_paid", "")
        digits = "".join(character for character in value if character.isdigit())

        if not digits:
            raise forms.ValidationError("Informe o valor pago da consulta.")

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
