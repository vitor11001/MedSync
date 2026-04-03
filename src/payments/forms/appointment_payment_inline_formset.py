from decimal import Decimal

from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet


class AppointmentPaymentInlineFormSet(BaseInlineFormSet):
    """Valida a consistência dos pagamentos vinculados à consulta."""

    def clean(self):
        """Garante que a consulta tenha pagamentos e que a soma feche o valor total."""
        super().clean()

        if any(self.errors):
            return

        total_amount = self.instance.total_amount
        payments_total = Decimal("0.00")
        valid_forms_count = 0

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue

            if form.cleaned_data.get("DELETE"):
                continue

            payment_method = form.cleaned_data.get("payment_method")
            amount = form.cleaned_data.get("amount")

            if payment_method is None and amount in (None, ""):
                continue

            valid_forms_count += 1
            payments_total += amount or Decimal("0.00")

        if valid_forms_count == 0:
            raise ValidationError("Informe ao menos um pagamento para a consulta.")

        if total_amount is None:
            return

        if payments_total != total_amount:
            raise ValidationError(
                "A soma dos pagamentos deve ser exatamente igual ao valor total da consulta."
            )
