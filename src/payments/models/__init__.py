"""Reexports do domínio financeiro enquanto o schema permanece no app clinic."""

from .appointment_payment import AppointmentPayment
from .doctor_payment_split_rule import DoctorPaymentSplitRule
from .payment_method import PaymentMethod

__all__ = [
    "AppointmentPayment",
    "DoctorPaymentSplitRule",
    "PaymentMethod",
]
