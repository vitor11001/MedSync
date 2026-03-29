from django.contrib import admin
from django.contrib.admin import helpers
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


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Configuração do admin para consultas."""

    change_list_template = "admin/clinic/appointment/change_list.html"
    form = AppointmentAdminForm
    autocomplete_fields = ("client", "doctor")
    readonly_fields = (
        "created_by",
        "code",
        "display_doctor_percentage",
        "display_clinic_percentage",
        "display_doctor_amount",
        "display_clinic_amount",
    )
    list_display = (
        "code",
        "client",
        "doctor",
        "created_by",
        "consultation_type",
        "amount_paid",
        "payment_method",
    )
    search_fields = ("code", "client__full_name", "doctor__full_name")
    list_filter = (
        "doctor",
        ("created_at", DateRangeFilterBuilder(title="periodo de criacao")),
    )
    editable_after_creation_fields = {"notes"}
    readonly_replacements = {
        "doctor_percentage": "display_doctor_percentage",
        "clinic_percentage": "display_clinic_percentage",
        "doctor_amount": "display_doctor_amount",
        "clinic_amount": "display_clinic_amount",
    }

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

    def _build_display_fields(self):
        """Monta a sequência base de campos exibidos no formulário do admin."""
        fields = list(self.form.base_fields.keys())
        fields.extend(self.readonly_fields)

        for original_field, display_field in self.readonly_replacements.items():
            original_index = fields.index(original_field) if original_field in fields else None
            fields = [
                field_name
                for field_name in fields
                if field_name not in {original_field, display_field}
            ]

            if original_index is not None:
                fields.insert(original_index, display_field)

        return fields

    def get_fields(self, request, obj=None):
        """Exibe o campo de auditoria apenas na edição."""
        fields = self._build_display_fields()

        if obj is None and "created_by" in fields:
            fields.remove("created_by")
        if obj is None and "code" in fields:
            fields.remove("code")
        if obj is None and "display_doctor_percentage" in fields:
            fields.remove("display_doctor_percentage")
        if obj is None and "display_clinic_percentage" in fields:
            fields.remove("display_clinic_percentage")
        if obj is None and "display_doctor_amount" in fields:
            fields.remove("display_doctor_amount")
        if obj is None and "display_clinic_amount" in fields:
            fields.remove("display_clinic_amount")

        return fields

    def get_readonly_fields(self, request, obj=None):
        """Permite edição apenas da observação para o criador da consulta."""
        readonly_fields = list(super().get_readonly_fields(request, obj))

        if obj is None:
            return tuple(readonly_fields)

        fields = self._build_display_fields()

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

    class Media:
        js = (
            "clinic/vendor/jquery.min.js",
            "clinic/vendor/jquery.mask.min.js",
            "clinic/admin/appointment_form.js",
        )
