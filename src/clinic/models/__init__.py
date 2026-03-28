"""Pacote de models do app de clinica."""

from .appointment import Appointment
from .client import Client
from .doctor import Doctor
from .email import Email
from .phone import Phone

__all__ = [
    "Appointment",
    "Client",
    "Doctor",
    "Email",
    "Phone",
]
