from django import forms
from django.contrib import admin

from clinic.models import DoctorPaymentSplitRule


class DoctorPaymentSplitRuleAdminForm(forms.ModelForm):
    """Formulário do admin para regras de repasse."""

    class Meta:
        model = DoctorPaymentSplitRule
        exclude = ("is_deleted", "deleted_at")


@admin.register(DoctorPaymentSplitRule)
class DoctorPaymentSplitRuleAdmin(admin.ModelAdmin):
    """Configuração do admin para regras de repasse."""

    form = DoctorPaymentSplitRuleAdminForm
    list_display = (
        "doctor",
        "payment_method",
        "doctor_percentage",
        "clinic_percentage",
        "is_active",
    )
    search_fields = ("doctor__full_name", "doctor__crm")
