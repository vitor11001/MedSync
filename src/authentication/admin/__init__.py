"""Pacote de administracao do app authentication."""

from .group import AuthenticationGroupAdmin
from .user import CustomUserAdmin

__all__ = ["AuthenticationGroupAdmin", "CustomUserAdmin"]
