"""Pacote de administracao do app clinic."""

from .appointment import AppointmentAdmin
from .client import ClientAdmin
from .doctor import DoctorAdmin
from .email import EmailAdmin
from .phone import PhoneAdmin

__all__ = [
    "AppointmentAdmin",
    "ClientAdmin",
    "DoctorAdmin",
    "EmailAdmin",
    "PhoneAdmin",
]
