"""Signals do app statistics."""

from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.practice.models import PracticeHistory

from .services import recalculate_statistics


@receiver(post_save, sender=PracticeHistory, dispatch_uid="update_statistics_on_practice")
def update_statistics_on_practice(
    sender: type, instance: PracticeHistory, created: bool, **kwargs: Any
) -> None:
    """Mantém o agregado do usuário atualizado a cada tentativa registrada."""
    if created:
        recalculate_statistics(instance.user)
