from datetime import date

from django.test import TestCase

from clinic.admin.client import ClientAdminForm
from clinic.models import Client


class ClientAdminFormTests(TestCase):
    """Tests for the patient admin form."""

    def test_formats_cpf_with_mask(self):
        """The form should normalize CPF to the expected mask."""
        form = ClientAdminForm(
            data={
                "full_name": "Maria Silva",
                "sex": Client.Sex.FEMALE,
                "cpf": "12345678901",
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["cpf"], "123.456.789-01")

    def test_rejects_invalid_cpf_length(self):
        """The form should reject CPF values with invalid length."""
        form = ClientAdminForm(
            data={
                "full_name": "Maria Silva",
                "sex": Client.Sex.FEMALE,
                "cpf": "1234",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("cpf", form.errors)

    def test_accepts_birth_date_in_brazilian_format(self):
        """The form should parse birth dates in dd/mm/yyyy format."""
        form = ClientAdminForm(
            data={
                "full_name": "Maria Silva",
                "birth_date": "25/12/1988",
                "sex": Client.Sex.FEMALE,
                "cpf": "12345678901",
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["birth_date"], date(1988, 12, 25))

    def test_rejects_birth_date_without_full_year(self):
        """The form should require a complete year in the birth date."""
        form = ClientAdminForm(
            data={
                "full_name": "Maria Silva",
                "birth_date": "01/03/98",
                "sex": Client.Sex.FEMALE,
                "cpf": "12345678901",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "Informe a data de nascimento com dia, mes e ano completos "
            "no formato dd/mm/aaaa.",
            form.errors["birth_date"],
        )


class ClientModelTests(TestCase):
    """Tests for patient model metadata."""

    def test_sex_field_uses_expected_choices(self):
        """The sex field should expose the configured choices."""
        choices = dict(Client._meta.get_field("sex").choices)

        self.assertEqual(
            choices,
            {
                Client.Sex.MALE: "Masculino",
                Client.Sex.FEMALE: "Feminino",
            },
        )
