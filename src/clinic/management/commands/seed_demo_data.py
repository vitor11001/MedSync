import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from clinic.models import (
    Appointment,
    Client,
    Doctor,
    DoctorPaymentSplitRule,
    Specialty,
)


class Command(BaseCommand):
    """Popula o banco com dados falsos para testes do fluxo da clínica."""

    help = "Create demo data for doctors, clients and appointments."
    SPECIALTY_NAMES = (
        "mastologista",
        "clinico geral",
        "medico do trabalho",
    )

    DOCTOR_DATA = [
        {
            "full_name": "Aluizio João da Silva Filho",
            "crm": "6654",
            "specialties": ["mastologista"],
        },
        {
            "full_name": "Marcos Antonio Pereira",
            "crm": "8123",
            "specialties": ["clinico geral"],
        },
        {
            "full_name": "Luciana Bezerra Costa",
            "crm": "9231",
            "specialties": ["medico do trabalho"],
        },
        {
            "full_name": "Patricia Andrade Lima",
            "crm": "10452",
            "specialties": ["clinico geral", "medico do trabalho"],
        },
    ]

    CLIENT_FIRST_NAMES = [
        "Ana",
        "Bruno",
        "Camila",
        "Daniel",
        "Eduarda",
        "Felipe",
        "Gabriela",
        "Henrique",
        "Isabela",
        "João",
        "Karina",
        "Lucas",
        "Marina",
        "Nicolas",
        "Otavio",
        "Priscila",
        "Rafaela",
        "Sergio",
        "Tatiane",
        "Vinicius",
    ]
    CLIENT_LAST_NAMES = [
        "Almeida",
        "Barbosa",
        "Cardoso",
        "Dias",
        "Esteves",
        "Ferreira",
        "Gomes",
        "Holanda",
        "Ibrahim",
        "Jardim",
        "Klein",
        "Leal",
        "Moura",
        "Nascimento",
        "Oliveira",
        "Pereira",
        "Queiroz",
        "Rocha",
        "Silva",
        "Teixeira",
    ]
    NOTES = [
        "",
        "Paciente relatou melhora importante desde o último atendimento.",
        "Solicitado retorno com exames laboratoriais atualizados.",
        "Necessário acompanhamento da evolução clínica nas próximas semanas.",
        "Atendimento realizado sem intercorrências e com boa adesão ao tratamento.",
    ]

    def add_arguments(self, parser):
        """Define os argumentos opcionais do comando."""
        parser.add_argument("--patients", type=int, default=30)
        parser.add_argument("--appointments", type=int, default=120)
        parser.add_argument("--days", type=int, default=45)
        parser.add_argument("--seed", type=int, default=42)

    def handle(self, *args, **options):
        """Cria dados falsos úteis para validar busca, filtros e relatórios."""
        random.seed(options["seed"])

        with transaction.atomic():
            specialties = self._ensure_specialties()
            doctors = self._ensure_doctors(specialties)
            self._ensure_payment_split_rules(doctors)
            clients = self._ensure_clients(options["patients"])
            receptionist = self._ensure_receptionist()
            appointments_count = self._ensure_appointments(
                doctors=doctors,
                clients=clients,
                receptionist=receptionist,
                appointments_count=options["appointments"],
                days=options["days"],
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Seed concluído com sucesso: "
                f"{len(specialties)} especialidades, "
                f"{len(doctors)} médicos, "
                f"{len(clients)} pacientes, "
                f"{appointments_count} consultas."
            )
        )

    def _ensure_specialties(self):
        """Garante as especialidades mínimas usadas pelos dados de teste."""
        specialties = {}

        for name in self.SPECIALTY_NAMES:
            specialty, _ = Specialty.objects.get_or_create(name=name)
            specialties[name] = specialty

        return specialties

    def _ensure_doctors(self, specialties):
        """Garante os médicos de teste com suas especialidades vinculadas."""
        doctors = []

        for doctor_data in self.DOCTOR_DATA:
            doctor, _ = Doctor.objects.get_or_create(
                crm=doctor_data["crm"],
                defaults={
                    "full_name": doctor_data["full_name"],
                    "phone_primary": self._generate_phone(),
                    "phone_secondary": "",
                    "email": self._build_email_from_name(doctor_data["full_name"]),
                    "notes": "",
                    "is_active": True,
                },
            )
            doctor.specialties.set(
                [specialties[name] for name in doctor_data["specialties"]]
            )
            doctors.append(doctor)

        return doctors

    def _ensure_payment_split_rules(self, doctors):
        """Garante regras de repasse para os médicos e pagamentos de teste."""
        payment_rules = {
            "6654": {
                Appointment.PaymentMethod.MONEY: ("70.00", "30.00"),
                Appointment.PaymentMethod.PIX: ("70.00", "30.00"),
                Appointment.PaymentMethod.CREDIT_CARD: ("65.00", "35.00"),
                Appointment.PaymentMethod.DEBIT_CARD: ("67.50", "32.50"),
                Appointment.PaymentMethod.HEALTH_INSURANCE: ("60.00", "40.00"),
            },
            "8123": {
                Appointment.PaymentMethod.MONEY: ("68.00", "32.00"),
                Appointment.PaymentMethod.PIX: ("68.00", "32.00"),
                Appointment.PaymentMethod.CREDIT_CARD: ("63.00", "37.00"),
                Appointment.PaymentMethod.DEBIT_CARD: ("64.50", "35.50"),
                Appointment.PaymentMethod.HEALTH_INSURANCE: ("58.00", "42.00"),
            },
            "9231": {
                Appointment.PaymentMethod.MONEY: ("66.00", "34.00"),
                Appointment.PaymentMethod.PIX: ("66.00", "34.00"),
                Appointment.PaymentMethod.CREDIT_CARD: ("62.00", "38.00"),
                Appointment.PaymentMethod.DEBIT_CARD: ("63.00", "37.00"),
                Appointment.PaymentMethod.HEALTH_INSURANCE: ("57.00", "43.00"),
            },
            "10452": {
                Appointment.PaymentMethod.MONEY: ("69.00", "31.00"),
                Appointment.PaymentMethod.PIX: ("69.00", "31.00"),
                Appointment.PaymentMethod.CREDIT_CARD: ("64.00", "36.00"),
                Appointment.PaymentMethod.DEBIT_CARD: ("65.00", "35.00"),
                Appointment.PaymentMethod.HEALTH_INSURANCE: ("59.00", "41.00"),
            },
        }

        for doctor in doctors:
            doctor_rules = payment_rules.get(doctor.crm, {})

            for payment_method, percentages in doctor_rules.items():
                DoctorPaymentSplitRule.objects.update_or_create(
                    doctor=doctor,
                    payment_method=payment_method,
                    defaults={
                        "doctor_percentage": Decimal(percentages[0]),
                        "clinic_percentage": Decimal(percentages[1]),
                        "is_active": True,
                    },
                )

    def _ensure_clients(self, patients_count):
        """Cria pacientes de teste até alcançar a quantidade desejada."""
        existing_clients = list(Client.objects.order_by("id"))

        while len(existing_clients) < patients_count:
            full_name = self._generate_client_name()
            cpf = self._generate_cpf(existing_clients_count=len(existing_clients) + 1)
            client = Client.objects.create(
                full_name=full_name,
                birth_date=self._generate_birth_date(),
                sex=random.choice([Client.Sex.MALE, Client.Sex.FEMALE]),
                cpf=cpf,
                phone_primary=self._generate_phone(),
                phone_secondary="",
                email=self._build_email_from_name(full_name, suffix=len(existing_clients) + 1),
                notes=random.choice(self.NOTES),
            )
            existing_clients.append(client)

        return existing_clients[:patients_count]

    def _ensure_receptionist(self):
        """Garante um usuário de recepção para criação das consultas falsas."""
        user_model = get_user_model()
        receptionist, created = user_model.objects.get_or_create(
            email="recepcao@example.com",
            defaults={
                "first_name": "Recepcao",
                "last_name": "Teste",
                "is_staff": True,
            },
        )

        if created:
            receptionist.set_password("Recepcao@12345")
            receptionist.save(update_fields=["password"])

        return receptionist

    def _ensure_appointments(self, *, doctors, clients, receptionist, appointments_count, days):
        """Cria consultas distribuídas no período desejado para testes."""
        current_count = Appointment.objects.count()

        while current_count < appointments_count:
            doctor = random.choice(doctors)
            client = random.choice(clients)
            created_at = self._generate_created_at(days=days)

            appointment = Appointment.objects.create(
                client=client,
                doctor=doctor,
                created_by=receptionist,
                code=Appointment._generate_code(sequence_date=created_at.date()),
                consultation_type=random.choice(
                    list(Appointment.ConsultationType.values)
                ),
                amount_paid=self._generate_amount(),
                payment_method=random.choice(list(Appointment.PaymentMethod.values)),
                notes=random.choice(self.NOTES),
            )
            Appointment.objects.filter(pk=appointment.pk).update(
                created_at=created_at,
                updated_at=created_at,
            )
            current_count += 1

        return appointments_count

    def _generate_client_name(self):
        """Gera um nome completo simples para os pacientes de teste."""
        return (
            f"{random.choice(self.CLIENT_FIRST_NAMES)} "
            f"{random.choice(self.CLIENT_LAST_NAMES)} "
            f"{random.choice(self.CLIENT_LAST_NAMES)}"
        )

    @staticmethod
    def _generate_cpf(existing_clients_count):
        """Gera um CPF formatado e determinístico para os dados de teste."""
        base_number = 10000000000 + existing_clients_count
        digits = str(base_number).zfill(11)[:11]
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"

    @staticmethod
    def _generate_phone():
        """Gera um telefone no formato esperado pelo sistema."""
        number = f"81{random.randint(900000000, 999999999)}"
        return f"({number[:2]}) {number[2:7]}-{number[7:]}"

    @staticmethod
    def _build_email_from_name(full_name, suffix=None):
        """Gera um email simples e previsível a partir do nome informado."""
        normalized_name = (
            full_name.lower()
            .replace(" ", ".")
            .replace("ã", "a")
            .replace("á", "a")
            .replace("à", "a")
            .replace("â", "a")
            .replace("é", "e")
            .replace("ê", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ô", "o")
            .replace("õ", "o")
            .replace("ú", "u")
            .replace("ç", "c")
        )
        suffix_part = f".{suffix}" if suffix else ""
        return f"{normalized_name}{suffix_part}@example.com"

    @staticmethod
    def _generate_amount():
        """Gera um valor pago plausível para as consultas de teste."""
        amount = Decimal(random.choice([120, 150, 180, 200, 250, 300]))
        cents = Decimal(random.choice(["0.00", "0.50"]))
        return amount + cents

    @staticmethod
    def _generate_created_at(*, days):
        """Gera uma data e hora de criação realista dentro do período informado."""
        day_offset = random.randint(0, max(days - 1, 0))
        appointment_date = timezone.localdate() - timedelta(days=day_offset)
        hour = random.randint(7, 17)
        minute = random.choice([0, 10, 20, 30, 40, 50])
        naive_datetime = datetime.combine(appointment_date, time(hour=hour, minute=minute))
        return timezone.make_aware(naive_datetime, timezone.get_current_timezone())

    @staticmethod
    def _generate_birth_date():
        """Gera uma data de nascimento plausível para os pacientes de teste."""
        today = timezone.localdate()
        age_in_days = random.randint(18 * 365, 85 * 365)
        return today - timedelta(days=age_in_days)
