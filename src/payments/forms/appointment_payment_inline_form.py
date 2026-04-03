from decimal import Decimal, InvalidOperation

from django import forms
from django.db.models import Q

from payments.models import AppointmentPayment, PaymentMethod


class AppointmentPaymentInlineForm(forms.ModelForm):
    """Formulário inline para os pagamentos da consulta."""

    amount = forms.CharField(
        label="valor pago (R$)",
        help_text="Informe apenas numeros. A virgula dos centavos sera aplicada automaticamente.",
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
        model = AppointmentPayment
        fields = ("payment_method", "amount")

    def __init__(self, *args, **kwargs):
        """Define o valor inicial formatado quando o item já existe."""
        super().__init__(*args, **kwargs)

        payment_methods = PaymentMethod.objects.filter(is_active=True)

        if self.instance.pk and self.instance.payment_method_id:
            payment_methods = PaymentMethod.objects.filter(
                Q(is_active=True) | Q(pk=self.instance.payment_method_id)
            )

        payment_method_field = self.fields.get("payment_method")
        if payment_method_field is not None:
            payment_method_field.queryset = payment_methods.order_by("name")

        if self.instance.pk and self.instance.amount is not None:
            self.initial["amount"] = self._format_amount(self.instance.amount)

    def clean_amount(self) -> Decimal:
        """Converte o valor formatado em decimal para persistência."""
        value = self.cleaned_data.get("amount", "")
        digits = "".join(character for character in value if character.isdigit())

        if not digits:
            raise forms.ValidationError("Informe o valor pago deste item.")

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
