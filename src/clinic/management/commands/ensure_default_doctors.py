from django.core.management.base import BaseCommand

from clinic.models import Doctor, Specialty


class Command(BaseCommand):
    """Garante o cadastro dos médicos padrão."""

    help = "Create the default doctors if they do not exist."

    def handle(self, *args, **options):
        """Cria o médico padrão informado pelo projeto."""
        mastologist, _ = Specialty.objects.get_or_create(name="Mastologista")

        doctor, created = Doctor.objects.get_or_create(
            crm="6654",
            defaults={
                "full_name": "Aluizio João da Silva Filho",
                "phone_primary": "",
                "phone_secondary": "",
                "email": "",
                "notes": "",
                "is_active": True,
            },
        )
        doctor.specialties.add(mastologist)

        if created:
            self.stdout.write(
                "Default doctor created: aluizio joão da silva filho (CRM 6654)"
            )
            return

        self.stdout.write("Default doctor already exists for CRM 6654.")
