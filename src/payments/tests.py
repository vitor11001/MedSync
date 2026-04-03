from django.core.exceptions import ValidationError
from django.test import TestCase

from payments.models import PaymentMethod


class PaymentMethodModelTests(TestCase):
    """Tests for payment method normalization and ordering."""

    def test_save_normalizes_name_to_lowercase_without_outer_spaces(self):
        """The model should trim and lowercase the payment method name on save."""
        payment_method = PaymentMethod.objects.create(name="  PIX  ", is_active=True)

        self.assertEqual(payment_method.name, "pix")

    def test_full_clean_rejects_duplicate_name_after_normalization(self):
        """The model should not allow duplicate names that normalize to the same value."""
        PaymentMethod.objects.create(name="pix", is_active=True)
        duplicate = PaymentMethod(name="  PIX  ", is_active=True)

        with self.assertRaises(ValidationError) as context:
            duplicate.full_clean()

        self.assertIn("name", context.exception.message_dict)

    def test_existing_payment_method_name_cannot_be_changed(self):
        """The payment method name should be immutable after creation."""
        payment_method = PaymentMethod.objects.create(name="pix", is_active=True)
        payment_method.name = "cartao"

        with self.assertRaises(ValidationError) as context:
            payment_method.save()

        self.assertIn("name", context.exception.message_dict)

    def test_name_field_uses_max_length_of_fifty_characters(self):
        """The payment method name should be limited to fifty characters."""
        field = PaymentMethod._meta.get_field("name")

        self.assertEqual(field.max_length, 50)

    def test_string_representation_uses_title_case_for_display(self):
        """The display string should keep storage lowercase but show title case."""
        payment_method = PaymentMethod.objects.create(
            name="boleto - teste interno",
            is_active=True,
        )

        self.assertEqual(str(payment_method), "Boleto - Teste Interno")

    def test_default_queryset_is_sorted_alphabetically_by_name(self):
        """The default ordering should follow the payment method name."""
        PaymentMethod.objects.create(name="zzz teste", is_active=True)
        PaymentMethod.objects.create(name="aaa teste", is_active=True)
        PaymentMethod.objects.create(name="mmm teste", is_active=True)

        self.assertEqual(
            list(
                PaymentMethod.objects.filter(name__in=["zzz teste", "aaa teste", "mmm teste"])
                .values_list("name", flat=True)
            ),
            ["aaa teste", "mmm teste", "zzz teste"],
        )
