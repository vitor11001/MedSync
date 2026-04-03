from django.contrib import admin

from payments.models import PaymentMethod


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Configuração do admin para formas de pagamento."""

    fields = ("name", "code", "is_active")
    list_display = ("display_name", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    ordering = ("name",)

    @admin.display(description="nome", ordering="name")
    def display_name(self, obj):
        """Exibe o nome da forma de pagamento com a primeira letra maiúscula."""
        return obj.display_name

    def get_readonly_fields(self, request, obj=None):
        """Mantém nome e código apenas como leitura após a criação."""
        readonly_fields = list(super().get_readonly_fields(request, obj))

        if obj is not None:
            readonly_fields.extend(["name", "code"])

        return tuple(dict.fromkeys(readonly_fields))
