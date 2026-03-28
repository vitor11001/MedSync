from typing import Self

from django.db import models
from django.utils import timezone

from .soft_delete_manager import SoftDeleteModelManager


class SoftDeleteModel(models.Model):
    """Model base para soft delete."""

    is_deleted = models.BooleanField("excluído", default=False)
    deleted_at = models.DateTimeField("excluído em", null=True, blank=True)

    all_objects = models.Manager()
    objects = SoftDeleteModelManager()

    class Meta:
        abstract = True

    def hard_delete(
        self,
        using: str | None = None,
        keep_parents: bool = False,
    ) -> tuple[int, dict[str, int]]:
        """Deleta permanentemente o registro."""
        return super().delete(using=using, keep_parents=keep_parents)

    def delete(self) -> None:
        """Soft delete por padrão."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def restore(self) -> Self:
        """Restaura um registro soft-deleted."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
        return self
