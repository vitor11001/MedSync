from decimal import Decimal

from django.contrib import admin
from django.contrib.admin import helpers
from django.db.models import Prefetch, Sum
from django.core.exceptions import PermissionDenied
from django.http import FileResponse
from django.template.response import TemplateResponse
from django.urls import path, reverse
from rangefilter.filters import DateRangeFilterBuilder

from clinic.controllers import (
    AppointmentReportDataController,
    AppointmentReportPdfController,
)
from clinic.forms import AppointmentAdminForm, AppointmentReportForm
from clinic.models import Appointment
from payments.forms import AppointmentPaymentInlineForm, AppointmentPaymentInlineFormSet
from payments.models import AppointmentPayment


class AppointmentPaymentInline(admin.TabularInline):
    """Exibe os pagamentos diretamente na tela da consulta."""

    model = AppointmentPayment
    form = AppointmentPaymentInlineForm
    formset = AppointmentPaymentInlineFormSet
    extra = 1
    min_num = 1
    validate_min = True
    can_delete = False
    verbose_name = "Pagamento"
    verbose_name_plural = "Pagamentos"
    readonly_fields = (
        "display_doctor_percentage",
        "display_clinic_percentage",
        "display_doctor_amount",
        "display_clinic_amount",
        "received_at",
        "created_by",
    )

    def get_queryset(self, request):
        """Evita consultas adicionais ao exibir os pagamentos existentes."""
        return super().get_queryset(request).select_related("created_by")

    def get_fields(self, request, obj=None):
        """Exibe apenas os campos necessários em cada estágio do fluxo."""
        if obj is None:
            return ("payment_method", "amount")

        return (
            "payment_method",
            "amount",
            "display_doctor_percentage",
            "display_clinic_percentage",
            "display_doctor_amount",
            "display_clinic_amount",
            "received_at",
            "created_by",
        )

    def get_readonly_fields(self, request, obj=None):
        """Trava a edição dos pagamentos após a criação da consulta."""
        if obj is None:
            return tuple()

        return (
            "payment_method",
            "amount",
            "display_doctor_percentage",
            "display_clinic_percentage",
            "display_doctor_amount",
            "display_clinic_amount",
            "received_at",
            "created_by",
        )

    def get_extra(self, request, obj=None, **kwargs):
        """Exibe linha em branco apenas na criação da consulta."""
        return 1 if obj is None else 0

    def has_add_permission(self, request, obj=None):
        """Permite incluir pagamentos apenas na criação da consulta."""
        return obj is None and super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """Impede remoção de pagamentos pelo admin."""
        return False

    @staticmethod
    def _format_decimal(value):
        """Formata decimal com vírgula para exibição no admin."""
        if value is None:
            return "-"

        return f"{value:.2f}".replace(".", ",")

    @admin.display(description="Percentual do médico (%)")
    def display_doctor_percentage(self, obj):
        """Exibe o percentual do médico com duas casas decimais."""
        return self._format_decimal(obj.doctor_percentage)

    @admin.display(description="Percentual da clínica (%)")
    def display_clinic_percentage(self, obj):
        """Exibe o percentual da clínica com duas casas decimais."""
        return self._format_decimal(obj.clinic_percentage)

    @admin.display(description="Valor do médico (R$)")
    def display_doctor_amount(self, obj):
        """Exibe o valor do médico com duas casas decimais."""
        return self._format_decimal(obj.doctor_amount)

    @admin.display(description="Valor da clínica (R$)")
    def display_clinic_amount(self, obj):
        """Exibe o valor da clínica com duas casas decimais."""
        return self._format_decimal(obj.clinic_amount)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Configuração do admin para consultas."""

    change_list_template = "admin/clinic/appointment/change_list.html"
    form = AppointmentAdminForm
    inlines = (AppointmentPaymentInline,)
    autocomplete_fields = ("client", "doctor")
    readonly_fields = (
        "created_by",
        "code",
        "display_total_paid",
        "display_doctor_total",
        "display_clinic_total",
    )
    list_display = (
        "code",
        "client",
        "doctor",
        "created_by",
        "consultation_type",
        "total_amount",
        "payments_summary",
    )
    search_fields = ("code", "client__full_name", "doctor__full_name")
    list_filter = (
        "doctor",
        ("created_at", DateRangeFilterBuilder(title="periodo de criacao")),
    )
    editable_after_creation_fields = {"notes"}

    def get_queryset(self, request):
        """Prefetch de relacionamentos usados na listagem e na edição."""
        return (
            super()
            .get_queryset(request)
            .select_related("client", "doctor", "created_by")
            .prefetch_related(
                Prefetch(
                    "payments",
                    queryset=AppointmentPayment.objects.select_related(
                        "created_by",
                        "payment_method",
                    ).order_by("received_at", "id"),
                )
            )
        )

    def get_urls(self):
        """Adiciona as URLs customizadas do admin de consultas."""
        custom_urls = [
            path(
                "report/",
                self.admin_site.admin_view(self.report_view),
                name="clinic_appointment_report",
            ),
        ]
        return custom_urls + super().get_urls()

    def changelist_view(self, request, extra_context=None):
        """Adiciona o link da página de relatório ao changelist."""
        extra_context = extra_context or {}
        extra_context["report_url"] = reverse("admin:clinic_appointment_report")
        return super().changelist_view(request, extra_context=extra_context)

    def report_view(self, request):
        """Exibe a página inicial de emissão do relatório em PDF."""
        form = AppointmentReportForm(request.POST or None)

        if request.method == "POST" and form.is_valid():
            report_scope = "all_doctors" if form.cleaned_data["doctor"] == "all" else "doctor"
            doctor = None if report_scope == "all_doctors" else form.cleaned_data["doctor"]

            data_controller = AppointmentReportDataController()
            report_data = data_controller.get_report_data(
                report_scope=report_scope,
                doctor=doctor,
                start_date=form.cleaned_data["start_date"],
                end_date=form.cleaned_data["end_date"],
            )
            pdf_controller = AppointmentReportPdfController()
            pdf_file = pdf_controller.generate_pdf(report_data)

            return FileResponse(
                pdf_file,
                as_attachment=False,
                filename=self._build_report_filename(report_data),
                content_type="application/pdf",
            )

        fieldsets = (
            (
                None,
                {
                    "fields": ("doctor", "start_date", "end_date"),
                },
            ),
        )
        admin_form = helpers.AdminForm(
            form=form,
            fieldsets=fieldsets,
            prepopulated_fields={},
            readonly_fields=(),
            model_admin=self,
        )

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Emitir relatório de consultas",
            "subtitle": "Escolha o médico e o período do relatório.",
            "form": form,
            "adminform": admin_form,
            "media": self.media + admin_form.media,
        }

        return TemplateResponse(
            request,
            "admin/clinic/appointment/report_form.html",
            context,
        )

    @staticmethod
    def _build_report_filename(report_data):
        """Monta o nome do arquivo PDF a partir do escopo e do período."""
        start_date = report_data["period"]["start_date"].replace("-", "")
        end_date = report_data["period"]["end_date"].replace("-", "")

        if report_data["scope"] == "doctor":
            doctor_name = report_data["header"]["doctor_name"].lower().replace(" ", "-")
            return f"relatorio-consultas-{doctor_name}-{start_date}-a-{end_date}.pdf"

        return f"relatorio-consultas-todos-os-medicos-{start_date}-a-{end_date}.pdf"

    def get_fields(self, request, obj=None):
        """Exibe apenas os campos adequados para criação ou visualização."""
        if obj is None:
            return (
                "client",
                "doctor",
                "consultation_type",
                "total_amount",
                "notes",
            )

        return (
            "client",
            "doctor",
            "created_by",
            "code",
            "consultation_type",
            "total_amount",
            "display_total_paid",
            "display_doctor_total",
            "display_clinic_total",
            "notes",
        )

    def get_readonly_fields(self, request, obj=None):
        """Permite edição apenas da observação para o criador da consulta."""
        readonly_fields = list(super().get_readonly_fields(request, obj))

        if obj is None:
            return tuple(readonly_fields)

        fields = list(self.get_fields(request, obj))

        if obj.created_by_id == request.user.id:
            return tuple(
                field_name
                for field_name in readonly_fields + fields
                if field_name not in self.editable_after_creation_fields
            )

        return tuple(dict.fromkeys(readonly_fields + fields))

    @staticmethod
    def _format_decimal(value):
        """Formata decimal com vírgula para exibição no admin."""
        if value is None:
            return "-"

        return f"{value:.2f}".replace(".", ",")

    @staticmethod
    def _sum_payment_values(obj, field_name):
        """Soma um campo dos pagamentos usando prefetch quando disponível."""
        prefetched_payments = getattr(obj, "_prefetched_objects_cache", {}).get("payments")

        if prefetched_payments is not None:
            return sum(
                (getattr(payment, field_name) for payment in prefetched_payments),
                start=Decimal("0.00"),
            )

        totals = obj.payments.aggregate(total=Sum(field_name))
        return totals["total"] or Decimal("0.00")

    @admin.display(description="Pagamentos")
    def payments_summary(self, obj):
        """Resume as formas de pagamento usadas na consulta."""
        prefetched_payments = getattr(obj, "_prefetched_objects_cache", {}).get("payments")
        payments = (
            prefetched_payments
            if prefetched_payments is not None
            else list(obj.payments.all())
        )

        if len(payments) == 0:
            return "-"

        return " | ".join(payment.payment_method_display for payment in payments)

    @admin.display(description="Total pago (R$)")
    def display_total_paid(self, obj):
        """Exibe a soma dos pagamentos registrados na consulta."""
        return self._format_decimal(self._sum_payment_values(obj, "amount"))

    @admin.display(description="Total do médico (R$)")
    def display_doctor_total(self, obj):
        """Exibe a soma destinada ao médico nesta consulta."""
        return self._format_decimal(self._sum_payment_values(obj, "doctor_amount"))

    @admin.display(description="Total da clínica (R$)")
    def display_clinic_total(self, obj):
        """Exibe a soma destinada à clínica nesta consulta."""
        return self._format_decimal(self._sum_payment_values(obj, "clinic_amount"))

    def save_model(self, request, obj, form, change):
        """Define o criador e impede edição indevida após a criação."""
        if not change and obj.created_by_id is None:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
            return

        if change:
            original_obj = Appointment.objects.get(pk=obj.pk)

            if original_obj.created_by_id != request.user.id:
                raise PermissionDenied(
                    "Apenas o usuário que criou a consulta pode alterar a observação."
                )

            changed_fields = set(form.changed_data)
            disallowed_fields = changed_fields - self.editable_after_creation_fields

            if disallowed_fields:
                raise PermissionDenied(
                    "Após criar a consulta, apenas a observação pode ser alterada."
                )

        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """Define o criador dos pagamentos gerados junto com a consulta."""
        instances = formset.save(commit=False)

        for deleted_object in formset.deleted_objects:
            deleted_object.delete()

        for instance in instances:
            if isinstance(instance, AppointmentPayment) and instance.created_by_id is None:
                instance.created_by = request.user
            instance.save()

        formset.save_m2m()

    class Media:
        js = (
            "clinic/vendor/jquery.min.js",
            "clinic/vendor/jquery.mask.min.js",
            "clinic/admin/appointment_form.js",
        )
