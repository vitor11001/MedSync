from django.core.management.base import BaseCommand

from payments.models import PaymentMethod


class Command(BaseCommand):
    """Garante o cadastro das formas de pagamento padrão."""

    help = "Create the default payment methods if they do not exist."

    DEFAULT_PAYMENT_METHODS = (
        {"name": "Pix - Casa Forte", "code": "pix"},
        {"name": "Cartão de crédito", "code": "credit_card"},
        {"name": "Cartão de débito", "code": "debit_card"},
        {"name": "Dinheiro", "code": "money"},
        {"name": "Pix - Maquineta", "code": "pix_maquineta"},
        {"name": "Plano de saúde", "code": "health_insurance"},
    )

    def handle(self, *args, **options):
        """Cria as formas de pagamento padrão ausentes."""
        created_names: list[str] = []

        for payment_method_data in self.DEFAULT_PAYMENT_METHODS:
            _, created = PaymentMethod.objects.update_or_create(
                code=payment_method_data["code"],
                defaults={
                    "name": payment_method_data["name"],
                    "is_active": True,
                },
            )

            if created:
                created_names.append(payment_method_data["name"])

        if created_names:
            self.stdout.write("Payment methods created: " + ", ".join(created_names))
            return

        self.stdout.write("All default payment methods already exist.")
