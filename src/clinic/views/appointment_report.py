from django.http import FileResponse
from rest_framework import permissions
from rest_framework.views import APIView

from clinic.controllers import (
    AppointmentReportDataController,
    AppointmentReportPdfController,
)
from clinic.serializers import AppointmentReportRequestSerializer


class AppointmentReportAPIView(APIView):
    """View de POST para preparar os dados do relatório de consultas."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Valida a entrada e delega a montagem dos dados do relatório."""
        serializer = AppointmentReportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data_controller = AppointmentReportDataController()
        report_data = data_controller.get_report_data(
            report_scope=serializer.validated_data["report_scope"],
            doctor=serializer.validated_data["doctor"],
            start_date=serializer.validated_data["start_date"],
            end_date=serializer.validated_data["end_date"],
        )
        pdf_controller = AppointmentReportPdfController()
        pdf_file = pdf_controller.generate_pdf(report_data)

        return FileResponse(
            pdf_file,
            as_attachment=False,
            filename=self._build_filename(report_data),
            content_type="application/pdf",
        )

    @staticmethod
    def _build_filename(report_data):
        """Monta o nome do arquivo PDF a partir do escopo e do período."""
        start_date = report_data["period"]["start_date"].replace("-", "")
        end_date = report_data["period"]["end_date"].replace("-", "")

        if report_data["scope"] == "doctor":
            doctor_name = report_data["header"]["doctor_name"].lower().replace(" ", "-")
            return f"relatorio-consultas-{doctor_name}-{start_date}-a-{end_date}.pdf"

        return f"relatorio-consultas-todos-os-medicos-{start_date}-a-{end_date}.pdf"
