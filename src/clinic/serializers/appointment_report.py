from datetime import timedelta

from rest_framework import serializers

from clinic.models import Doctor


class AppointmentReportRequestSerializer(serializers.Serializer):
    """Serializer de entrada para a emissão do relatório de consultas."""

    class ReportScope(serializers.ChoiceField):
        """Campo de escolha do escopo do relatório."""

    report_scope = serializers.ChoiceField(
        choices=(
            ("all_doctors", "Todos os médicos"),
            ("doctor", "Médico específico"),
        )
    )
    doctor_id = serializers.IntegerField(required=False, allow_null=True)
    start_date = serializers.DateField(input_formats=["%d/%m/%Y", "%Y-%m-%d"])
    end_date = serializers.DateField(input_formats=["%d/%m/%Y", "%Y-%m-%d"])

    def validate(self, attrs):
        """Valida as regras de escopo e período do relatório."""
        start_date = attrs["start_date"]
        end_date = attrs["end_date"]
        report_scope = attrs["report_scope"]
        doctor_id = attrs.get("doctor_id")

        if start_date > end_date:
            raise serializers.ValidationError(
                {"end_date": "A data final deve ser maior ou igual à data inicial."}
            )

        if end_date - start_date > timedelta(days=92):
            raise serializers.ValidationError(
                {"end_date": "O período máximo permitido para o relatório é de 3 meses."}
            )

        if report_scope == "doctor":
            if not doctor_id:
                raise serializers.ValidationError(
                    {"doctor_id": "Informe o médico para emitir o relatório individual."}
                )

            try:
                attrs["doctor"] = Doctor.objects.get(pk=doctor_id)
            except Doctor.DoesNotExist as exc:
                raise serializers.ValidationError(
                    {"doctor_id": "Selecione um médico válido."}
                ) from exc
        else:
            attrs["doctor"] = None

        return attrs
