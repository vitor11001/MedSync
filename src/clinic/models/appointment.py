from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
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
    amount_paid = models.DecimalField(
        "valor pago",
        max_digits=10,
        decimal_places=2,
        help_text="Valor pago pelo paciente na consulta.",
    )
    doctor_percentage = models.DecimalField(
        "percentual do médico",
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentual do valor pago destinado ao médico na criação da consulta.",
    )
    clinic_percentage = models.DecimalField(
        "percentual da clínica",
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentual do valor pago destinado à clínica na criação da consulta.",
    )
    doctor_amount = models.DecimalField(
        "valor do médico",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valor destinado ao médico na criação da consulta.",
    )
    clinic_amount = models.DecimalField(
        "valor da clínica",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valor destinado à clínica na criação da consulta.",
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

    def save(self, *args, **kwargs):
        """Gera o código e congela o repasse financeiro apenas na criação da consulta."""
        is_new = self.pk is None

        if is_new and not self.code:
            self.code = self._generate_code()
        if is_new:
            self.apply_payment_split_snapshot()

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

    def apply_payment_split_snapshot(self):
        """Calcula e congela na consulta o repasse do médico e da clínica.

        Os percentuais são lidos da regra ativa do médico para a forma de
        pagamento da consulta. Se houver diferença de arredondamento de centavos,
        o ajuste final é aplicado ao valor da clínica, garantindo que a soma feche
        exatamente no total pago e que a clínica fique com o centavo residual.
        """
        rule = self._get_active_payment_split_rule()

        doctor_percentage = rule.doctor_percentage
        clinic_percentage = rule.clinic_percentage

        raw_doctor_amount = self.amount_paid * doctor_percentage / Decimal("100")
        raw_clinic_amount = self.amount_paid * clinic_percentage / Decimal("100")

        doctor_amount = raw_doctor_amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        clinic_amount = raw_clinic_amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        difference = self.amount_paid - (doctor_amount + clinic_amount)
        clinic_amount = (clinic_amount + difference).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        self.doctor_percentage = doctor_percentage
        self.clinic_percentage = clinic_percentage
        self.doctor_amount = doctor_amount
        self.clinic_amount = clinic_amount

    def _get_active_payment_split_rule(self):
        """Busca a regra ativa de repasse para o médico e a forma de pagamento."""
        from clinic.models import DoctorPaymentSplitRule

        try:
            return DoctorPaymentSplitRule.objects.get(
                doctor=self.doctor,
                payment_method=self.payment_method,
                is_active=True,
            )
        except DoctorPaymentSplitRule.DoesNotExist as exc:
            raise ValidationError(
                "Não existe regra de repasse ativa para este médico e esta forma de pagamento."
            ) from exc

    def __str__(self) -> str:
        """Retorna a representação textual da consulta."""
        return f"{self.code} | {self.client} - {self.doctor}"
