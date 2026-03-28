from django.db import models

from _seed.models import BaseModelDjango, SoftDeleteModel


class Client(BaseModelDjango, SoftDeleteModel):
    """Model que representa o paciente."""

    full_name = models.CharField(
        "nome completo",
        max_length=255,
        help_text="Nome completo do paciente.",
    )
    birth_date = models.DateField(
        "data de nascimento",
        null=True,
        blank=True,
        help_text="Data de nascimento do paciente.",
    )
    sex = models.CharField(
        "sexo",
        max_length=20,
        null=True,
        blank=True,
        help_text="Sexo do paciente.",
    )
    cpf = models.CharField(
        "cpf",
        max_length=14,
        null=True,
        blank=True,
        help_text="CPF do paciente.",
    )
    phones = models.ManyToManyField(
        "clinic.Phone",
        verbose_name="telefones",
        related_name="clients",
        blank=True,
        help_text="Telefones vinculados ao paciente.",
    )
    emails = models.ManyToManyField(
        "clinic.Email",
        verbose_name="emails",
        related_name="clients",
        blank=True,
        help_text="Emails vinculados ao paciente.",
    )
    notes = models.TextField(
        "observacao",
        null=True,
        blank=True,
        help_text="Observacoes gerais sobre o paciente.",
    )

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

    def __str__(self) -> str:
        """Retorna a representacao textual do paciente."""
        return self.full_name
