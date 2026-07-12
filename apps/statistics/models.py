"""Modelos do app statistics — desempenho agregado por usuário (Fase 5)."""

from django.conf import settings
from django.db import models


class UserStatistics(models.Model):
    """Agregado de desempenho do usuário (um registro por usuário).

    Recalculado internamente a partir de ``PracticeHistory`` (ver
    ``services.recalculate_statistics``) — nunca recebe escrita direta do
    cliente; a API expõe somente leitura.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="statistics",
    )
    characters_seen = models.PositiveIntegerField(default=0)  # tentativas registradas
    characters_correct = models.PositiveIntegerField(default=0)
    accuracy = models.FloatField(default=0.0)  # fração 0.0–1.0
    average_speed = models.FloatField(default=0.0)  # caracteres por minuto
    training_time = models.PositiveBigIntegerField(default=0)  # soma dos response_time (ms)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "user statistics"

    def __str__(self) -> str:
        return f"Estatísticas de {self.user}"
