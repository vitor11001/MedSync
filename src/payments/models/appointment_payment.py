from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from _seed.models import BaseModelDjango


class AppointmentPayment(BaseModelDjango):
    """Representa um item de pagamento vinculado a uma consulta."""

    DEFAULT_DOCTOR_PERCENTAGE = Decimal("70.00")
    DEFAULT_CLINIC_PERCENTAGE = Decimal("30.00")

    appointment = models.ForeignKey(
        "clinic.Appointment",
        verbose_name="consulta",
        on_delete=models.PROTECT,
        related_name="payments",
        help_text="Consulta à qual este pagamento pertence.",
    )
    created_by = models.ForeignKey(
        "authentication.User",
        verbose_name="criado por",
        on_delete=models.SET_NULL,
        related_name="created_appointment_payments",
        null=True,
        blank=True,
        help_text="Usuario que registrou este pagamento.",
    )
    payment_method = models.ForeignKey(
        "payments.PaymentMethod",
        verbose_name="forma de pagamento",
        on_delete=models.PROTECT,
        related_name="appointment_payments",
        help_text="Forma de pagamento utilizada neste item.",
    )
    payment_method_name_snapshot = models.CharField(
        "nome da forma de pagamento",
        max_length=100,
        blank=True,
        help_text="Nome da forma de pagamento congelado no momento do lançamento.",
    )
    amount = models.DecimalField(
        "valor pago",
        max_digits=10,
        decimal_places=2,
        help_text="Valor pago neste item de pagamento.",
    )
    doctor_percentage = models.DecimalField(
        "percentual do médico",
        max_digits=5,
        decimal_places=2,
        help_text="Percentual do item destinado ao médico no momento do lançamento.",
    )
    clinic_percentage = models.DecimalField(
        "percentual da clínica",
        max_digits=5,
        decimal_places=2,
        help_text="Percentual do item destinado à clínica no momento do lançamento.",
    )
    doctor_amount = models.DecimalField(
        "valor do médico",
        max_digits=10,
        decimal_places=2,
        help_text="Valor do item destinado ao médico.",
    )
    clinic_amount = models.DecimalField(
        "valor da clínica",
        max_digits=10,
        decimal_places=2,
        help_text="Valor do item destinado à clínica.",
    )
    received_at = models.DateTimeField(
        "recebido em",
        default=timezone.now,
        help_text="Data e hora em que o pagamento foi registrado.",
    )

    class Meta:
        verbose_name = "Pagamento da consulta"
        verbose_name_plural = "Pagamentos das consultas"
        db_table = "clinic_appointmentpayment"

    def clean(self):
        """Valida se o pagamento possui uma consulta e um valor válido."""
        if self.amount is not None and self.amount <= Decimal("0.00"):
            raise ValidationError({"amount": "Informe um valor maior que zero."})

        if self.appointment_id is None and self.appointment is None:
            raise ValidationError({"appointment": "Selecione a consulta do pagamento."})

    def save(self, *args, **kwargs):
        """Congela o snapshot financeiro do item de pagamento ao salvar."""
        if (
            self._state.adding
            and self.payment_method_id
            and not self.payment_method_name_snapshot
        ):
            self.payment_method_name_snapshot = self.payment_method.name

        self.apply_payment_split_snapshot()
        super().save(*args, **kwargs)

    def apply_payment_split_snapshot(self):
        """Calcula e congela o repasse do médico e da clínica para este item."""
        if self.amount is None:
            return

        rule = self._get_active_payment_split_rule()
        doctor_percentage = rule.doctor_percentage
        clinic_percentage = rule.clinic_percentage

        raw_doctor_amount = self.amount * doctor_percentage / Decimal("100")
        raw_clinic_amount = self.amount * clinic_percentage / Decimal("100")

        doctor_amount = raw_doctor_amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        clinic_amount = raw_clinic_amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        difference = self.amount - (doctor_amount + clinic_amount)
        clinic_amount = (clinic_amount + difference).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        self.doctor_percentage = doctor_percentage
        self.clinic_percentage = clinic_percentage
        self.doctor_amount = doctor_amount
        self.clinic_amount = clinic_amount

    def _get_active_payment_split_rule(self):
        """Busca a regra ativa do médico para a forma de pagamento deste item."""
        from payments.models import DoctorPaymentSplitRule

        try:
            return DoctorPaymentSplitRule.objects.get(
                doctor=self.appointment.doctor,
                payment_method=self.payment_method,
                is_active=True,
            )
        except DoctorPaymentSplitRule.DoesNotExist:
            return type(
                "DefaultPaymentSplitRule",
                (),
                {
                    "doctor_percentage": self.DEFAULT_DOCTOR_PERCENTAGE,
                    "clinic_percentage": self.DEFAULT_CLINIC_PERCENTAGE,
                },
            )()

    @property
    def payment_method_display(self) -> str:
        """Retorna o nome histórico da forma de pagamento do item."""
        if self.payment_method_name_snapshot:
            return self.payment_method_name_snapshot

        if self.payment_method_id:
            return self.payment_method.name

        return "-"

    def __str__(self) -> str:
        """Retorna a representação textual do item de pagamento."""
        return (
            f"{self.appointment.code} | {self.payment_method_display} | "
            f"R$ {self.amount:.2f}"
        )


__all__ = ["AppointmentPayment"]
