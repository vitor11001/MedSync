from django.contrib import admin

from clinic.forms import DoctorPaymentSplitRuleAdminForm
from clinic.models import DoctorPaymentSplitRule


@admin.register(DoctorPaymentSplitRule)
class DoctorPaymentSplitRuleAdmin(admin.ModelAdmin):
    """Configuração do admin para regras de repasse."""

    form = DoctorPaymentSplitRuleAdminForm
    fields = (
        "doctor",
        "payment_method",
        "doctor_percentage",
        "clinic_percentage",
        "is_active",
    )
    list_display = (
        "doctor",
        "payment_method",
        "doctor_percentage",
        "clinic_percentage",
        "is_active",
    )
    search_fields = ("doctor__full_name", "doctor__crm")

    def get_readonly_fields(self, request, obj=None):
        """Impede troca do médico e da forma de pagamento após a criação."""
        readonly_fields = list(super().get_readonly_fields(request, obj))

        if obj is not None:
            readonly_fields.extend(["doctor", "payment_method"])

        return tuple(dict.fromkeys(readonly_fields))

    class Media:
        js = (
            "clinic/vendor/jquery.min.js",
            "clinic/vendor/jquery.mask.min.js",
            "clinic/admin/doctor_payment_split_rule_form.js",
        )
