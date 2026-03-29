from django.core.management.base import BaseCommand

from clinic.models import Specialty


class Command(BaseCommand):
    """Garante o cadastro das especialidades padrão."""

    help = "Create the default specialties if they do not exist."

    DEFAULT_SPECIALTIES = (
        "Mastologista",
        "Clinico Geral",
        "Medico do Trabalho",
    )

    def handle(self, *args, **options):
        """Cria as especialidades padrão ausentes."""
        created_names: list[str] = []

        for specialty_name in self.DEFAULT_SPECIALTIES:
            _, created = Specialty.objects.get_or_create(name=specialty_name)

            if created:
                created_names.append(specialty_name)

        if created_names:
            self.stdout.write(
                "Specialties created: " + ", ".join(created_names)
            )
            return

        self.stdout.write("All default specialties already exist.")
