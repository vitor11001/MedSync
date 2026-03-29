"""Pacote de controllers do app clinic."""

from .appointment_report_data import AppointmentReportDataController
from .appointment_report_pdf import AppointmentReportPdfController

__all__ = ["AppointmentReportDataController", "AppointmentReportPdfController"]
