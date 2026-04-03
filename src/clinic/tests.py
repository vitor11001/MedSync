from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory
from django.test import TestCase
from django.urls import reverse

from clinic.controllers import AppointmentReportDataController
from clinic.forms import (
    ClientAdminForm,
)
from clinic.models import (
    Appointment,
    Client,
    Doctor,
)
from payments.forms import AppointmentPaymentInlineForm, AppointmentPaymentInlineFormSet
from payments.models import AppointmentPayment, DoctorPaymentSplitRule, PaymentMethod


class AppointmentAdminTests(TestCase):
    """Regression tests for the appointment admin screen."""

    def setUp(self):
        """Create the records needed to open the admin change form."""
        user_model = get_user_model()
        self.admin_user = user_model.objects.create_superuser(
            email="admin@example.com",
            password="secret123",
        )
        self.creator = user_model.objects.create_user(
            email="creator@example.com",
            password="secret123",
        )
        self.patient = Client.objects.create(
            full_name="Maria da Silva",
            birth_date=date(1990, 1, 1),
            sex=Client.Sex.FEMALE,
            phone_primary="(81) 99999-9999",
        )
        self.doctor = Doctor.objects.create(
            full_name="Joao Medico",
            crm="12345",
            phone_primary="(81) 98888-7777",
            is_active=True,
        )
        self.appointment = Appointment.objects.create(
            client=self.patient,
            doctor=self.doctor,
            created_by=self.creator,
            consultation_type=Appointment.ConsultationType.FIRST_CONSULTATION,
            total_amount=Decimal("300.00"),
            notes="Consulta inicial",
        )

    def test_change_view_loads_for_non_creator_user(self):
        """The admin page should render for users other than the creator."""
        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("admin:clinic_appointment_change", args=[self.appointment.pk])
        )

        self.assertEqual(response.status_code, 200)


class ClientAdminFormTests(TestCase):
    """Tests for the patient admin form."""

    def test_formats_cpf_with_mask(self):
        """The form should normalize CPF to the expected mask."""
        form = ClientAdminForm(
            data={
                "full_name": "Maria Silva",
                "birth_date": "25/12/1988",
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
                "birth_date": "25/12/1988",
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


class AppointmentPaymentModelTests(TestCase):
    """Tests for payment split snapshots per payment item."""

    def setUp(self):
        """Cria os dados base para as consultas financeiras."""
        self.client = Client.objects.create(
            full_name="Maria da Silva",
            birth_date=date(1990, 1, 1),
            sex=Client.Sex.FEMALE,
            phone_primary="(81) 99999-9999",
        )
        self.doctor = Doctor.objects.create(
            full_name="Joao Medico",
            crm="12345",
            phone_primary="(81) 98888-7777",
            is_active=True,
        )
        self.money, _ = PaymentMethod.objects.get_or_create(
            code="money",
            defaults={"name": "Dinheiro", "is_active": True},
        )
        self.credit_card, _ = PaymentMethod.objects.get_or_create(
            code="credit_card",
            defaults={
                "name": "Cartão de crédito",
                "is_active": True,
            },
        )

    def test_applies_split_rule_per_payment_method(self):
        """Each payment item should freeze the rule of its own payment method."""
        DoctorPaymentSplitRule.objects.create(
            doctor=self.doctor,
            payment_method=self.money,
            doctor_percentage=Decimal("70.00"),
            clinic_percentage=Decimal("30.00"),
        )
        DoctorPaymentSplitRule.objects.create(
            doctor=self.doctor,
            payment_method=self.credit_card,
            doctor_percentage=Decimal("65.00"),
            clinic_percentage=Decimal("35.00"),
        )
        appointment = Appointment.objects.create(
            client=self.client,
            doctor=self.doctor,
            consultation_type=Appointment.ConsultationType.FIRST_CONSULTATION,
            total_amount=Decimal("300.00"),
        )

        money_payment = AppointmentPayment.objects.create(
            appointment=appointment,
            payment_method=self.money,
            amount=Decimal("200.00"),
        )
        card_payment = AppointmentPayment.objects.create(
            appointment=appointment,
            payment_method=self.credit_card,
            amount=Decimal("100.00"),
        )

        self.assertEqual(money_payment.doctor_percentage, Decimal("70.00"))
        self.assertEqual(money_payment.doctor_amount, Decimal("140.00"))
        self.assertEqual(money_payment.clinic_amount, Decimal("60.00"))
        self.assertEqual(card_payment.doctor_percentage, Decimal("65.00"))
        self.assertEqual(card_payment.doctor_amount, Decimal("65.00"))
        self.assertEqual(card_payment.clinic_amount, Decimal("35.00"))

    def test_keeps_payment_method_name_snapshot_after_direct_database_rename(self):
        """The payment should preserve the original payment method name."""
        DoctorPaymentSplitRule.objects.create(
            doctor=self.doctor,
            payment_method=self.money,
            doctor_percentage=Decimal("70.00"),
            clinic_percentage=Decimal("30.00"),
        )
        appointment = Appointment.objects.create(
            client=self.client,
            doctor=self.doctor,
            consultation_type=Appointment.ConsultationType.FIRST_CONSULTATION,
            total_amount=Decimal("100.00"),
        )

        payment = AppointmentPayment.objects.create(
            appointment=appointment,
            payment_method=self.money,
            amount=Decimal("100.00"),
        )

        PaymentMethod.objects.filter(pk=self.money.pk).update(name="dinheiro em especie")
        payment.refresh_from_db()

        self.assertEqual(payment.payment_method_name_snapshot, "dinheiro")
        self.assertEqual(payment.payment_method_display, "dinheiro")


class AppointmentPaymentInlineFormSetTests(TestCase):
    """Tests for the inline validation used in the admin."""

    def setUp(self):
        """Cria os dados mínimos para testar o formset inline."""
        self.client = Client.objects.create(
            full_name="Maria da Silva",
            birth_date=date(1990, 1, 1),
            sex=Client.Sex.FEMALE,
            phone_primary="(81) 99999-9999",
        )
        self.doctor = Doctor.objects.create(
            full_name="Joao Medico",
            crm="12345",
            phone_primary="(81) 98888-7777",
            is_active=True,
        )
        self.money, _ = PaymentMethod.objects.get_or_create(
            code="money",
            defaults={"name": "Dinheiro", "is_active": True},
        )
        self.credit_card, _ = PaymentMethod.objects.get_or_create(
            code="credit_card",
            defaults={
                "name": "Cartão de crédito",
                "is_active": True,
            },
        )
        self.formset_class = inlineformset_factory(
            Appointment,
            AppointmentPayment,
            form=AppointmentPaymentInlineForm,
            formset=AppointmentPaymentInlineFormSet,
            fields=("payment_method", "amount"),
            extra=0,
            can_delete=False,
        )

    def test_accepts_payments_that_match_consultation_total(self):
        """The inline should accept payments whose sum matches the consultation total."""
        appointment = Appointment(
            client=self.client,
            doctor=self.doctor,
            consultation_type=Appointment.ConsultationType.FIRST_CONSULTATION,
            total_amount=Decimal("300.00"),
        )
        formset = self.formset_class(
            data={
                "payments-TOTAL_FORMS": "2",
                "payments-INITIAL_FORMS": "0",
                "payments-MIN_NUM_FORMS": "0",
                "payments-MAX_NUM_FORMS": "1000",
                "payments-0-payment_method": str(self.money.pk),
                "payments-0-amount": "200,00",
                "payments-1-payment_method": str(self.credit_card.pk),
                "payments-1-amount": "100,00",
            },
            instance=appointment,
            prefix="payments",
        )

        self.assertTrue(formset.is_valid())

    def test_rejects_payments_when_sum_differs_from_consultation_total(self):
        """The inline should reject payments whose sum differs from the consultation total."""
        appointment = Appointment(
            client=self.client,
            doctor=self.doctor,
            consultation_type=Appointment.ConsultationType.FIRST_CONSULTATION,
            total_amount=Decimal("300.00"),
        )
        formset = self.formset_class(
            data={
                "payments-TOTAL_FORMS": "2",
                "payments-INITIAL_FORMS": "0",
                "payments-MIN_NUM_FORMS": "0",
                "payments-MAX_NUM_FORMS": "1000",
                "payments-0-payment_method": str(self.money.pk),
                "payments-0-amount": "200,00",
                "payments-1-payment_method": str(self.credit_card.pk),
                "payments-1-amount": "90,00",
            },
            instance=appointment,
            prefix="payments",
        )

        self.assertFalse(formset.is_valid())
        self.assertIn(
            "A soma dos pagamentos deve ser exatamente igual ao valor total da consulta.",
            formset.non_form_errors(),
        )


class AppointmentReportDataControllerTests(TestCase):
    """Tests for the appointment report aggregation using multiple payments."""

    def setUp(self):
        """Cria uma consulta paga com duas formas de pagamento."""
        self.client = Client.objects.create(
            full_name="Maria da Silva",
            birth_date=date(1990, 1, 1),
            sex=Client.Sex.FEMALE,
            phone_primary="(81) 99999-9999",
        )
        self.doctor = Doctor.objects.create(
            full_name="Joao Medico",
            crm="12345",
            phone_primary="(81) 98888-7777",
            is_active=True,
        )
        self.money, _ = PaymentMethod.objects.get_or_create(
            code="money",
            defaults={"name": "Dinheiro", "is_active": True},
        )
        self.credit_card, _ = PaymentMethod.objects.get_or_create(
            code="credit_card",
            defaults={
                "name": "Cartão de crédito",
                "is_active": True,
            },
        )
        DoctorPaymentSplitRule.objects.create(
            doctor=self.doctor,
            payment_method=self.money,
            doctor_percentage=Decimal("70.00"),
            clinic_percentage=Decimal("30.00"),
        )
        DoctorPaymentSplitRule.objects.create(
            doctor=self.doctor,
            payment_method=self.credit_card,
            doctor_percentage=Decimal("65.00"),
            clinic_percentage=Decimal("35.00"),
        )
        self.appointment = Appointment.objects.create(
            client=self.client,
            doctor=self.doctor,
            consultation_type=Appointment.ConsultationType.FIRST_CONSULTATION,
            total_amount=Decimal("300.00"),
        )
        AppointmentPayment.objects.create(
            appointment=self.appointment,
            payment_method=self.money,
            amount=Decimal("200.00"),
        )
        AppointmentPayment.objects.create(
            appointment=self.appointment,
            payment_method=self.credit_card,
            amount=Decimal("100.00"),
        )

    def test_report_repeats_consultation_for_each_payment_item(self):
        """The report should render one row per payment item."""
        controller = AppointmentReportDataController()

        report = controller.get_report_data(
            report_scope="doctor",
            doctor=self.doctor,
            start_date=date.today(),
            end_date=date.today(),
        )

        self.assertEqual(len(report["rows"]), 2)
        self.assertEqual(report["rows"][0]["Nº"], 1)
        self.assertEqual(report["rows"][1]["Nº"], 1)
        self.assertEqual(report["rows"][0]["Código"], self.appointment.code)
        self.assertEqual(report["rows"][1]["Código"], self.appointment.code)
        self.assertEqual(report["rows"][0]["Pagamento"], "dinheiro")
        self.assertEqual(report["rows"][0]["Valor Total"], "200,00")
        self.assertEqual(report["rows"][0]["Valor Médico"], "140,00")
        self.assertEqual(report["rows"][0]["Valor Clínica"], "60,00")
        self.assertEqual(report["rows"][1]["Pagamento"], "cartão de crédito")
        self.assertEqual(report["rows"][1]["Valor Total"], "100,00")
        self.assertEqual(report["rows"][1]["Valor Médico"], "65,00")
        self.assertEqual(report["rows"][1]["Valor Clínica"], "35,00")
        self.assertEqual(report["totals"]["doctor_total"], "205,00")
        self.assertEqual(report["totals"]["clinic_total"], "95,00")
        self.assertEqual(report["totals"]["grand_total"], "300,00")
        self.assertEqual(
            report["totals"]["by_payment_method"],
            [
                {"label": "cartão de crédito", "value": "100,00"},
                {"label": "dinheiro", "value": "200,00"},
            ],
        )
