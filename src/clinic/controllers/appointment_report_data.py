from collections import defaultdict
from decimal import Decimal

from clinic.models import Appointment


class AppointmentReportDataController:
    """Controller responsável por montar os dados do relatório de consultas."""

    COMPANY_NAME = "MedSync"

    def get_report_data(self, *, report_scope, doctor, start_date, end_date):
        """Retorna os dados do relatório no formato adequado ao escopo solicitado."""
        queryset = (
            Appointment.objects.select_related("client", "doctor", "created_by")
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
                "appointments_count": len(rows),
            },
            "columns": ["Nº", "Código", "Paciente", "Tipo", "Pagamento", "Valor", "Observação"],
            "rows": rows,
            "totals": self._build_totals(appointments),
        }

    def _build_all_doctors_report(self, *, queryset, start_date, end_date):
        """Monta a estrutura de dados para o relatório de todos os médicos."""
        grouped_appointments = defaultdict(list)

        for appointment in queryset:
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

        all_appointments = list(queryset)

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
            "columns": ["Nº", "Código", "Paciente", "Tipo", "Pagamento", "Valor", "Observação"],
            "doctors": doctors,
            "totals": self._build_totals(all_appointments),
        }

    def _serialize_appointments(self, appointments):
        """Serializa a lista de consultas com numeração sequencial do relatório."""
        return [
            self._serialize_appointment(number=index, appointment=appointment)
            for index, appointment in enumerate(appointments, start=1)
        ]

    @staticmethod
    def _build_totals(appointments):
        """Calcula os totais por forma de pagamento e o faturamento geral."""
        totals_by_payment_method = defaultdict(lambda: Decimal("0.00"))
        grand_total = Decimal("0.00")

        for appointment in appointments:
            payment_method = appointment.get_payment_method_display()
            totals_by_payment_method[payment_method] += appointment.amount_paid
            grand_total += appointment.amount_paid

        return {
            "by_payment_method": [
                {
                    "label": label,
                    "value": f"{value:.2f}".replace(".", ","),
                }
                for label, value in totals_by_payment_method.items()
            ],
            "grand_total": f"{grand_total:.2f}".replace(".", ","),
        }

    @staticmethod
    def _serialize_appointment(*, number, appointment):
        """Serializa os dados da consulta no formato esperado pela tabela do relatório."""
        notes = (appointment.notes or "")[:100]

        return {
            "Nº": number,
            "Código": appointment.code,
            "Paciente": appointment.client.full_name.title(),
            "Tipo": appointment.get_consultation_type_display(),
            "Pagamento": appointment.get_payment_method_display(),
            "Valor": f"{appointment.amount_paid:.2f}".replace(".", ","),
            "Observação": notes,
        }
