from django.db import models

from _seed.models import BaseModelDjango, SoftDeleteModel


class Email(BaseModelDjango, SoftDeleteModel):
    """Model que representa um email."""

    email = models.EmailField(
        "email",
        help_text="Endereco de email cadastrado.",
    )

    class Meta:
        verbose_name = "Email"
        verbose_name_plural = "Emails"

    def __str__(self) -> str:
        """Retorna a representacao textual do email."""
        return self.email
