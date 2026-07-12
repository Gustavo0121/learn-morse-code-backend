"""Serviços de domínio do app morse."""

from typing import TYPE_CHECKING

from .models import UserMorseSettings

if TYPE_CHECKING:
    from apps.accounts.models import User


def ensure_default_settings(user: "User") -> UserMorseSettings:
    """Garante que o usuário tenha configurações de Morse (cria as padrão).

    Chamado na criação do usuário (signal) e como fallback na leitura do
    endpoint, para cobrir usuários criados antes da Fase 2.
    """
    settings, _created = UserMorseSettings.objects.get_or_create(user=user)
    return settings
