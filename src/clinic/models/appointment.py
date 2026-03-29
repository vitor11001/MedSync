from django.db import models

from _seed.models import BaseModelDjango, SoftDeleteModel


class Appointment(BaseModelDjango, SoftDeleteModel):
    """Model que representa a consulta."""

    class ConsultationType(models.TextChoices):
        """Opções de tipo de consulta."""

        FIRST_CONSULTATION = "first_consultation", "Primeira consulta"
        RETURN = "return", "Retorno"

    class PaymentMethod(models.TextChoices):
        """Opções de forma de pagamento."""

        MONEY = "money", "Dinheiro"
        PIX = "pix", "Pix"
        CREDIT_CARD = "credit_card", "Cartao de Credito"
        DEBIT_CARD = "debit_card", "Cartao de Debito"
        HEALTH_INSURANCE = "health_insurance", "Plano de Saude"

    client = models.ForeignKey(
        "clinic.Client",
        verbose_name="paciente",
        on_delete=models.PROTECT,
        related_name="appointments",
        help_text="Paciente vinculado a consulta.",
    )
    doctor = models.ForeignKey(
        "clinic.Doctor",
        verbose_name="medico",
        on_delete=models.PROTECT,
        related_name="appointments",
        help_text="Medico responsavel pela consulta.",
    )
    created_by = models.ForeignKey(
        "authentication.User",
        verbose_name="criado por",
        on_delete=models.SET_NULL,
        related_name="created_appointments",
        null=True,
        blank=True,
        help_text="Usuario que criou a consulta.",
    )
    consultation_type = models.CharField(
        "tipo de consulta",
        max_length=30,
        choices=ConsultationType.choices,
        help_text="Tipo da consulta realizada.",
    )
    amount_paid = models.DecimalField(
        "valor pago",
        max_digits=10,
        decimal_places=2,
        help_text="Valor pago pelo paciente na consulta.",
    )
    payment_method = models.CharField(
        "forma de pagamento",
        max_length=20,
        choices=PaymentMethod.choices,
        help_text="Forma de pagamento utilizada na consulta.",
    )
    notes = models.TextField(
        "observacao",
        null=True,
        blank=True,
        help_text="Observacoes gerais sobre a consulta.",
    )

    class Meta:
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"

    def __str__(self) -> str:
        """Retorna a representação textual da consulta."""
        return f"{self.client} - {self.doctor}"
