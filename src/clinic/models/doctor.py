from django.db import models

from _seed.models import BaseModelDjango, SoftDeleteModel


class Doctor(BaseModelDjango, SoftDeleteModel):
    """Model que representa o médico."""

    full_name = models.CharField(
        "nome completo",
        max_length=255,
        help_text="Nome completo do medico.",
    )
    specialties = models.ManyToManyField(
        "clinic.Specialty",
        verbose_name="especialidades",
        related_name="doctors",
        blank=True,
        help_text="Especialidades vinculadas ao medico.",
    )
    crm = models.CharField(
        "crm",
        max_length=50,
        help_text="Numero de registro CRM do medico.",
    )
    phone_primary = models.CharField(
        "telefone principal",
        max_length=20,
        blank=True,
        help_text="Telefone principal do medico.",
    )
    phone_secondary = models.CharField(
        "telefone secundario",
        max_length=20,
        blank=True,
        help_text="Telefone secundario do medico.",
    )
    email = models.EmailField(
        "email",
        blank=True,
        help_text="Email do medico.",
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

    def save(self, *args, **kwargs):
        """Normaliza o nome do médico antes de salvar."""
        self.full_name = self.full_name.strip().lower()
        super().save(*args, **kwargs)

    def specialties_display(self) -> str:
        """Retorna as especialidades do médico em texto simples."""
        return ", ".join(
            self.specialties.order_by("name").values_list("name", flat=True)
        )

    def __str__(self) -> str:
        """Retorna a representação textual do médico."""
        display_name = self.full_name.title()
        return f"{display_name} | CRM: {self.crm}"
