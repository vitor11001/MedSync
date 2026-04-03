from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Prefetch

from clinic.models import Appointment
from payments.models import AppointmentPayment


class AppointmentReportDataController:
    """Controller responsável por montar os dados do relatório de consultas."""

    COMPANY_NAME = "MedSync"
    REPORT_COLUMNS = [
        "Nº",
        "Código",
        "Paciente",
        "Tipo",
        "Pagamento",
        "Valor Total",
        "Valor Médico",
        "Valor Clínica",
        "Observação",
    ]

    def get_report_data(self, *, report_scope, doctor, start_date, end_date):
        """Retorna os dados do relatório no formato adequado ao escopo solicitado."""
        queryset = (
            Appointment.objects.select_related("client", "doctor", "created_by")
            .prefetch_related(
                Prefetch(
                    "payments",
                    queryset=AppointmentPayment.objects.select_related(
                        "payment_method"
                    ).order_by("received_at", "id"),
                )
            )
            .filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date,
            )
            .order_by("created_at", "doctor__full_name", "client__full_name")
        )

        if report_scope == "doctor":
            queryset = queryset.filter(doctor=doctor)
            return self._build_single_doctor_report(
                queryset=queryset,
                doctor=doctor,
                start_date=start_date,
                end_date=end_date,
            )

        return self._build_all_doctors_report(
            queryset=queryset,
            start_date=start_date,
            end_date=end_date,
        )

    def _build_single_doctor_report(self, *, queryset, doctor, start_date, end_date):
        """Monta a estrutura de dados para o relatório de um médico específico."""
        appointments = list(queryset)
        rows = self._serialize_appointments(queryset)

        return {
            "scope": "doctor",
            "header": {
                "company_name": self.COMPANY_NAME,
                "doctor_name": doctor.full_name.title(),
                "doctor_crm": doctor.crm,
                "start_date": start_date.strftime("%d/%m/%Y"),
                "end_date": end_date.strftime("%d/%m/%Y"),
            },
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "summary": {
                "appointments_count": len(appointments),
            },
            "columns": self.REPORT_COLUMNS,
            "rows": rows,
            "totals": self._build_totals(appointments),
        }

    def _build_all_doctors_report(self, *, queryset, start_date, end_date):
        """Monta a estrutura de dados para o relatório de todos os médicos."""
        appointments = list(queryset)
        grouped_appointments = defaultdict(list)

        for appointment in appointments:
            grouped_appointments[appointment.doctor].append(appointment)

        doctors = [
            {
                "header": {
                    "company_name": self.COMPANY_NAME,
                    "doctor_name": doctor.full_name.title(),
                    "doctor_crm": doctor.crm,
                    "start_date": start_date.strftime("%d/%m/%Y"),
                    "end_date": end_date.strftime("%d/%m/%Y"),
                },
                "appointments_count": len(appointments),
                "rows": self._serialize_appointments(appointments),
                "totals": self._build_totals(appointments),
            }
            for doctor, appointments in grouped_appointments.items()
        ]

        return {
            "scope": "all_doctors",
            "header": {
                "company_name": self.COMPANY_NAME,
                "doctor_name": "Todos os médicos",
                "doctor_crm": None,
                "start_date": start_date.strftime("%d/%m/%Y"),
                "end_date": end_date.strftime("%d/%m/%Y"),
            },
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "summary": {
                "appointments_count": sum(
                    doctor_data["appointments_count"] for doctor_data in doctors
                ),
                "doctors_count": len(doctors),
            },
            "columns": self.REPORT_COLUMNS,
            "doctors": doctors,
            "totals": self._build_totals(appointments),
        }

    def _serialize_appointments(self, appointments):
        """Serializa a lista de consultas em linhas por item de pagamento."""
        rows = []

        for appointment_number, appointment in enumerate(appointments, start=1):
            for payment in appointment.payments.all():
                rows.append(
                    self._serialize_payment_row(
                        number=appointment_number,
                        appointment=appointment,
                        payment=payment,
                    )
                )

        return rows

    @staticmethod
    def _build_totals(appointments):
        """Calcula os totais por forma de pagamento e o faturamento geral."""
        totals_by_payment_method = {}
        grand_total = Decimal("0.00")
        doctor_total = Decimal("0.00")
        clinic_total = Decimal("0.00")

        for appointment in appointments:
            payments = list(appointment.payments.all())

            for payment in payments:
                grand_total += payment.amount
                doctor_total += payment.doctor_amount
                clinic_total += payment.clinic_amount

                label = payment.payment_method_display

                if label not in totals_by_payment_method:
                    totals_by_payment_method[label] = {
                        "value": Decimal("0.00"),
                    }

                totals_by_payment_method[label]["value"] += payment.amount

        if grand_total > Decimal("0.00"):
            doctor_percentage = (
                (doctor_total / grand_total) * Decimal("100")
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            clinic_percentage = (
                (clinic_total / grand_total) * Decimal("100")
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            doctor_percentage = Decimal("0.00")
            clinic_percentage = Decimal("0.00")

        return {
            "by_payment_method": [
                {
                    "label": label,
                    "value": f"{data['value']:.2f}".replace(".", ","),
                }
                for label, data in sorted(
                    totals_by_payment_method.items(),
                    key=lambda item: item[0],
                )
            ],
            "doctor_total": f"{doctor_total:.2f}".replace(".", ","),
            "clinic_total": f"{clinic_total:.2f}".replace(".", ","),
            "doctor_percentage": f"{doctor_percentage:.2f}".replace(".", ","),
            "clinic_percentage": f"{clinic_percentage:.2f}".replace(".", ","),
            "grand_total": f"{grand_total:.2f}".replace(".", ","),
        }

    @staticmethod
    def _serialize_payment_row(*, number, appointment, payment):
        """Serializa uma linha do relatório a partir de um item de pagamento."""
        return {
            "Nº": number,
            "Código": appointment.code,
            "Paciente": appointment.client.full_name.title(),
            "Tipo": appointment.get_consultation_type_display(),
            "Pagamento": payment.payment_method_display,
            "Valor Total": f"{payment.amount:.2f}".replace(".", ","),
            "Valor Médico": f"{payment.doctor_amount:.2f}".replace(".", ","),
            "Valor Clínica": f"{payment.clinic_amount:.2f}".replace(".", ","),
            "Observação": (appointment.notes or "")[:100],
        }
