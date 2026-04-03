from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from _seed.models import BaseModelDjango


class DoctorPaymentSplitRule(BaseModelDjango):
    """Define a regra de repasse de um médico por forma de pagamento."""

    doctor = models.ForeignKey(
        "clinic.Doctor",
        verbose_name="médico",
        on_delete=models.PROTECT,
        related_name="payment_split_rules",
        help_text="Médico ao qual a regra de repasse pertence.",
    )
    payment_method = models.ForeignKey(
        "payments.PaymentMethod",
        verbose_name="forma de pagamento",
        on_delete=models.PROTECT,
        related_name="doctor_payment_split_rules",
        help_text="Forma de pagamento coberta por esta regra.",
    )
    doctor_percentage = models.DecimalField(
        "percentual do médico",
        max_digits=5,
        decimal_places=2,
        help_text="Percentual do valor pago que pertence ao médico.",
    )
    clinic_percentage = models.DecimalField(
        "percentual da clínica",
        max_digits=5,
        decimal_places=2,
        help_text="Percentual do valor pago que pertence à clínica.",
    )
    is_active = models.BooleanField(
        "ativo",
        default=True,
        help_text="Indica se esta regra pode ser usada nas novas consultas.",
    )

    class Meta:
        verbose_name = "Regra de repasse"
        verbose_name_plural = "Regras de repasse"
        db_table = "clinic_doctorpaymentsplitrule"
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "payment_method"],
                condition=models.Q(is_active=True),
                name="unique_active_split_rule_per_doctor_payment_method",
            ),
        ]

    def clean(self):
        """Valida se a soma dos percentuais da regra é exatamente 100."""
        total = (self.doctor_percentage or Decimal("0")) + (
            self.clinic_percentage or Decimal("0")
        )

        if total != Decimal("100"):
            raise ValidationError(
                "A soma do percentual do médico com o da clínica deve ser 100."
            )

    def __str__(self) -> str:
        """Retorna a representação textual da regra de repasse."""
        return (
            f"{self.doctor} | {self.payment_method.name} | "
            f"Médico {self.doctor_percentage}% | Clínica {self.clinic_percentage}%"
        )


__all__ = ["DoctorPaymentSplitRule"]
