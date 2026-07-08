"""Signals do app morse."""

from typing import Any

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .services import ensure_default_settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL, dispatch_uid="create_default_morse_settings")
def create_default_morse_settings(
    sender: type, instance: Any, created: bool, **kwargs: Any
) -> None:
    """Cria as configurações padrão de Morse ao criar um usuário."""
    if created:
        ensure_default_settings(instance)
