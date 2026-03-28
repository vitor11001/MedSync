from django.db import models

from _seed.models import BaseModelDjango, SoftDeleteModel


class Doctor(BaseModelDjango, SoftDeleteModel):
    """Model que representa o medico."""

    full_name = models.CharField(
        "nome completo",
        max_length=255,
        help_text="Nome completo do medico.",
    )
    specialty = models.CharField(
        "especialidade",
        max_length=255,
        help_text="Especialidade principal do medico.",
    )
    crm = models.CharField(
        "crm",
        max_length=50,
        help_text="Numero de registro CRM do medico.",
    )
    phones = models.ManyToManyField(
        "clinic.Phone",
        verbose_name="telefones",
        related_name="doctors",
        blank=True,
        help_text="Telefones vinculados ao medico.",
    )
    emails = models.ManyToManyField(
        "clinic.Email",
        verbose_name="emails",
        related_name="doctors",
        blank=True,
        help_text="Emails vinculados ao medico.",
    )
    notes = models.TextField(
        "observacao",
        null=True,
        blank=True,
        help_text="Observacoes gerais sobre o medico.",
    )
    is_active = models.BooleanField(
        "ativo",
        default=True,
        help_text="Indica se o medico esta ativo para atendimento.",
    )

    class Meta:
        verbose_name = "Medico"
        verbose_name_plural = "Medicos"

    def __str__(self) -> str:
        """Retorna a representacao textual do medico."""
        return self.full_name
