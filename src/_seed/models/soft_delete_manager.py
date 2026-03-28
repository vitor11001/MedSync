from django.db import models
from django.db.models import QuerySet


class SoftDeleteModelManager(models.Manager):
    """Manager que filtra registros deletados por padrão."""

    def get_queryset(self) -> QuerySet:
        """Retorna apenas registros não deletados."""
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self) -> QuerySet:
        """Retorna todos os registros, incluindo deletados."""
        return super().get_queryset()

    def deleted_only(self) -> QuerySet:
        """Retorna apenas registros deletados."""
        return super().get_queryset().filter(is_deleted=True)

