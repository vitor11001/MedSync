from django.db import models

from _seed.models import BaseModelDjango, SoftDeleteModel


class Phone(BaseModelDjango, SoftDeleteModel):
    """Model que representa um telefone."""

    number = models.CharField(
        "numero",
        max_length=20,
        help_text="Numero de telefone cadastrado.",
    )

    class Meta:
        verbose_name = "Telefone"
        verbose_name_plural = "Telefones"

    def __str__(self) -> str:
        """Retorna a representacao textual do telefone."""
        return self.number
