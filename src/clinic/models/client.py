from django.db import models

from _seed.models import BaseModelDjango, SoftDeleteModel


class Client(BaseModelDjango, SoftDeleteModel):
    """Model que representa o paciente."""

    class Sex(models.TextChoices):
        """Opções de sexo do paciente."""

        MALE = "male", "Masculino"
        FEMALE = "female", "Feminino"

    full_name = models.CharField(
        "nome completo",
        max_length=255,
        help_text="Nome completo do paciente.",
    )
    birth_date = models.DateField(
        "data de nascimento",
        help_text="Data de nascimento do paciente.",
    )
    sex = models.CharField(
        "sexo",
        max_length=20,
        choices=Sex.choices,
        help_text="Sexo do paciente.",
    )
    cpf = models.CharField(
        "cpf",
        max_length=14,
        null=True,
        blank=True,
        help_text="CPF do paciente.",
    )
    phone_primary = models.CharField(
        "telefone principal",
        max_length=20,
        blank=True,
        help_text="Telefone principal do paciente.",
    )
    phone_secondary = models.CharField(
        "telefone secundario",
        max_length=20,
        blank=True,
        help_text="Telefone secundario do paciente.",
    )
    email = models.EmailField(
        "email",
        blank=True,
        help_text="Email do paciente.",
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

    def save(self, *args, **kwargs):
        """Normaliza o nome do paciente antes de salvar."""
        self.full_name = self.full_name.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Retorna a representação textual do paciente."""
        display_name = self.full_name.title()
        display_cpf = self.cpf or "nao informado"
        return f"{display_name} | CPF: {display_cpf}"
