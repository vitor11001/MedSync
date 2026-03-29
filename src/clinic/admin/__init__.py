"""Pacote de administração do app clinic."""

from .appointment import AppointmentAdmin
from .client import ClientAdmin
from .doctor import DoctorAdmin
from .specialty import SpecialtyAdmin

__all__ = [
    "AppointmentAdmin",
    "ClientAdmin",
    "DoctorAdmin",
    "SpecialtyAdmin",
]
