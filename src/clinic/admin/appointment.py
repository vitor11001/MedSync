from django.contrib import admin

from clinic.models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Configuracao do admin para consultas."""

    list_display = (
        "client",
        "doctor",
        "consultation_type",
        "amount_paid",
        "payment_method",
        "is_deleted",
    )
    search_fields = ("client__full_name", "doctor__full_name")
    list_filter = ("consultation_type", "payment_method", "is_deleted", "created_at")
