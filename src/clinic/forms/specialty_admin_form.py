from django import forms

from clinic.models import Specialty


class SpecialtyAdminForm(forms.ModelForm):
    """Formulário do admin para especialidades."""

    class Meta:
        model = Specialty
        exclude = ("is_deleted", "deleted_at")
