from django.db import models

from _seed.models import BaseModelDjango, SoftDeleteModel


class Specialty(BaseModelDjango, SoftDeleteModel):
    """Model que representa uma especialidade médica."""

    name = models.CharField(
        "nome",
        max_length=255,
        unique=True,
        help_text="Nome da especialidade medica.",
    )

    class Meta:
        verbose_name = "Especialidade"
        verbose_name_plural = "Especialidades"

    def save(self, *args, **kwargs):
        """Normaliza o nome da especialidade antes de salvar."""
        self.name = self.name.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Retorna a representação textual da especialidade."""
        return self.name.title()
