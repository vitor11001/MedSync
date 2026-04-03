from decimal import Decimal

from django.db import models, transaction
from django.utils import timezone

from _seed.models import BaseModelDjango, SoftDeleteModel


class AppointmentDailySequence(models.Model):
    """Controla a sequência diária usada para gerar códigos únicos de consultas."""

    sequence_date = models.DateField("data da sequência", unique=True)
    last_value = models.PositiveIntegerField("último valor", default=0)

    class Meta:
        verbose_name = "Sequência diária de consulta"
        verbose_name_plural = "Sequências diárias de consulta"

    def __str__(self) -> str:
        """Retorna a representação textual da sequência diária."""
        return f"{self.sequence_date} - {self.last_value}"


class Appointment(BaseModelDjango, SoftDeleteModel):
    """Model que representa a consulta."""

    class ConsultationType(models.TextChoices):
        """Opções de tipo de consulta."""

        FIRST_CONSULTATION = "first_consultation", "Primeira consulta"
        RETURN = "return", "Retorno"
        ASO = "aso", "ASO"
        PROCEDURE = "procedure", "Procedimento"

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
    code = models.CharField(
        "código da consulta",
        max_length=20,
        unique=True,
        blank=True,
        editable=False,
        help_text="Código único para localização operacional da consulta.",
    )
    consultation_type = models.CharField(
        "tipo de consulta",
        max_length=30,
        choices=ConsultationType.choices,
        help_text="Tipo da consulta realizada.",
    )
    total_amount = models.DecimalField(
        "valor total",
        max_digits=10,
        decimal_places=2,
        help_text="Valor total da consulta, que deve bater com a soma dos pagamentos.",
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

    def save(self, *args, **kwargs):
        """Gera o código da consulta apenas na criação."""
        is_new = self.pk is None

        if is_new and not self.code:
            self.code = self._generate_code()

        super().save(*args, **kwargs)

    @classmethod
    def _generate_code(cls, sequence_date=None) -> str:
        """Gera um código diário único com trava transacional para evitar colisões.

        A criação de consultas pode acontecer ao mesmo tempo por mais de uma
        recepcionista. Por isso, a sequência do dia é buscada com
        `select_for_update()` dentro de uma transação atômica. Assim, apenas uma
        transação por vez incrementa o contador diário e duas consultas não recebem
        o mesmo código.
        """
        sequence_date = sequence_date or timezone.localdate()

        with transaction.atomic():
            sequence, _ = AppointmentDailySequence.objects.select_for_update().get_or_create(
                sequence_date=sequence_date,
                defaults={"last_value": 0},
            )
            sequence.last_value += 1
            sequence.save(update_fields=["last_value"])
            sequence_value = sequence.last_value

        return f"C-{sequence_date.strftime('%Y%m%d')}-{sequence_value:04d}"

    @property
    def total_paid(self):
        """Retorna a soma já carregada ou calculada dos pagamentos da consulta."""
        prefetched_payments = getattr(self, "_prefetched_objects_cache", {}).get("payments")

        if prefetched_payments is not None:
            return sum(
                (payment.amount for payment in prefetched_payments),
                start=Decimal("0.00"),
            )

        totals = self.payments.aggregate(total=models.Sum("amount"))
        return totals["total"] or Decimal("0.00")

    def __str__(self) -> str:
        """Retorna a representação textual da consulta."""
        return f"{self.code} | {self.client} - {self.doctor}"
