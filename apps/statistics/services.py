"""Serviço de agregação do app statistics.

Recalcula ``UserStatistics`` a partir de ``PracticeHistory`` — síncrono no
MVP; candidato a processamento assíncrono (Redis/Celery) no futuro.
"""

from typing import TYPE_CHECKING

from django.db.models import Count, Q, Sum

from apps.practice.models import PracticeHistory

from .models import UserStatistics

if TYPE_CHECKING:
    from apps.accounts.models import User

MS_PER_MINUTE = 60_000


def ensure_statistics(user: "User") -> UserStatistics:
    """Garante que o usuário tenha o registro agregado (cria zerado)."""
    statistics, _created = UserStatistics.objects.get_or_create(user=user)
    return statistics


def recalculate_statistics(user: "User") -> UserStatistics:
    """Recalcula o agregado do usuário a partir de todo o seu histórico.

    - ``accuracy``: fração de tentativas corretas (0.0–1.0).
    - ``training_time``: soma dos tempos de resposta, em ms.
    - ``average_speed``: caracteres por minuto, derivada do tempo total de
      resposta (nunca de valores enviados pelo cliente).
    """
    totals = PracticeHistory.objects.filter(user=user).aggregate(
        seen=Count("id"),
        correct=Count("id", filter=Q(correct=True)),
        time=Sum("response_time"),
    )
    seen: int = totals["seen"]
    correct: int = totals["correct"]
    training_time: int = totals["time"] or 0

    statistics = ensure_statistics(user)
    statistics.characters_seen = seen
    statistics.characters_correct = correct
    statistics.accuracy = correct / seen if seen else 0.0
    statistics.training_time = training_time
    statistics.average_speed = seen * MS_PER_MINUTE / training_time if training_time else 0.0
    statistics.save()
    return statistics
