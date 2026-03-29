from datetime import timedelta

from django import forms
from django.contrib.admin.widgets import AdminDateWidget

from clinic.models import Doctor


class AppointmentReportForm(forms.Form):
    """Formulário para emissão do relatório de consultas."""

    doctor = forms.ChoiceField(
        label="Médico",
        required=True,
        help_text="Selecione um médico específico ou a opção para incluir todos.",
    )
    start_date = forms.DateField(
        label="Data inicial",
        input_formats=["%d/%m/%Y"],
        widget=AdminDateWidget(
            attrs={"placeholder": "dd/mm/aaaa"},
        ),
        help_text="Informe a data inicial do período.",
        error_messages={
            "invalid": "Informe a data inicial no formato dd/mm/aaaa.",
            "required": "Informe a data inicial do relatório.",
        },
    )
    end_date = forms.DateField(
        label="Data final",
        input_formats=["%d/%m/%Y"],
        widget=AdminDateWidget(
            attrs={"placeholder": "dd/mm/aaaa"},
        ),
        help_text="Informe a data final do período.",
        error_messages={
            "invalid": "Informe a data final no formato dd/mm/aaaa.",
            "required": "Informe a data final do relatório.",
        },
    )

    def clean(self):
        """Valida o intervalo de datas permitido para o relatório."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if not start_date or not end_date:
            return cleaned_data

        if start_date > end_date:
            raise forms.ValidationError(
                "A data inicial não pode ser maior que a data final."
            )

        if end_date - start_date > timedelta(days=92):
            raise forms.ValidationError(
                "O período máximo permitido para o relatório é de 3 meses."
            )

        return cleaned_data

    def __init__(self, *args, **kwargs):
        """Carrega as opções disponíveis de médicos no formulário."""
        super().__init__(*args, **kwargs)
        self.fields["doctor"].choices = [
            ("all", "Todos os médicos"),
            *[
                (str(doctor.pk), str(doctor))
                for doctor in Doctor.objects.order_by("full_name")
            ],
        ]

    def clean_doctor(self):
        """Converte a seleção do médico para o objeto correspondente quando necessário."""
        value = self.cleaned_data["doctor"]

        if value == "all":
            return "all"

        try:
            return Doctor.objects.get(pk=value)
        except Doctor.DoesNotExist as exc:
            raise forms.ValidationError("Selecione um médico válido.") from exc
