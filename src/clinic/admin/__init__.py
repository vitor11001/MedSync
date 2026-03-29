"""Pacote de administração do app clinic."""

from .appointment import AppointmentAdmin
from .client import ClientAdmin
from .doctor import DoctorAdmin
from .doctor_payment_split_rule import DoctorPaymentSplitRuleAdmin
from .specialty import SpecialtyAdmin

__all__ = [
    "AppointmentAdmin",
    "ClientAdmin",
    "DoctorAdmin",
    "DoctorPaymentSplitRuleAdmin",
    "SpecialtyAdmin",
]
