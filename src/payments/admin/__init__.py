"""Pacote de administração do app payments."""

from .doctor_payment_split_rule import DoctorPaymentSplitRuleAdmin
from .payment_method import PaymentMethodAdmin

__all__ = [
    "DoctorPaymentSplitRuleAdmin",
    "PaymentMethodAdmin",
]
