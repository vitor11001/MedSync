from django.urls import path

from clinic.views import AppointmentReportAPIView


urlpatterns = [
    path(
        "reports/appointments/",
        AppointmentReportAPIView.as_view(),
        name="clinic-appointment-report-api",
    ),
]
