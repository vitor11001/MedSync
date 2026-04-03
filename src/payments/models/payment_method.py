from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from _seed.models import BaseModelDjango


class PaymentMethod(BaseModelDjango):
    """Representa uma forma de pagamento disponível na clínica."""

    name = models.CharField(
        "nome",
        max_length=50,
        unique=True,
        help_text="Nome exibido para a forma de pagamento.",
    )
    code = models.SlugField(
        "código",
        max_length=100,
        unique=True,
        blank=True,
        help_text="Identificador interno estável da forma de pagamento.",
    )
    is_active = models.BooleanField(
        "ativo",
        default=True,
        help_text="Indica se a forma de pagamento pode ser usada em novos lançamentos.",
    )

    class Meta:
        verbose_name = "Forma de pagamento"
        verbose_name_plural = "Formas de pagamento"
        ordering = ("name",)
        db_table = "clinic_paymentmethod"

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normaliza o nome para armazenamento consistente."""
        return name.strip().lower()

    def _validate_name_is_immutable(self):
        """Impede alteração do nome após a criação da forma de pagamento."""
        if not self.pk:
            return

        original_name = (
            PaymentMethod.objects.filter(pk=self.pk).values_list("name", flat=True).first()
        )

        if original_name is not None and original_name != self.name:
            raise ValidationError(
                {"name": "O nome da forma de pagamento não pode ser alterado."}
            )

    def clean(self):
        """Normaliza o nome e impede valores vazios após o trim."""
        super().clean()
        self.name = self._normalize_name(self.name)

        if not self.name:
            raise ValidationError({"name": "Informe o nome da forma de pagamento."})

        self._validate_name_is_immutable()

    def save(self, *args, **kwargs):
        """Gera um código estável a partir do nome quando necessário."""
        self.name = self._normalize_name(self.name)
        self._validate_name_is_immutable()

        if not self.code:
            base_code = slugify(self.name) or "forma-pagamento"
            code = base_code
            suffix = 2

            while PaymentMethod.objects.exclude(pk=self.pk).filter(code=code).exists():
                code = f"{base_code}-{suffix}"
                suffix += 1

            self.code = code

        super().save(*args, **kwargs)

    @property
    def display_name(self) -> str:
        """Retorna o nome formatado para exibição humana."""
        if not self.name:
            return ""

        return self.name.title()

    def __str__(self) -> str:
        """Retorna o nome da forma de pagamento."""
        return self.display_name


__all__ = ["PaymentMethod"]
