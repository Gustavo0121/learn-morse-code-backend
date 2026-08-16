"""Serviço de agregação do leaderboard.

Diferente de ``apps.statistics`` (agregado do usuário autenticado, recalculado
por signal e persistido), o leaderboard é uma consulta cross-user computada
sob demanda a partir de ``PracticeHistory`` — sem model próprio.
"""

from datetime import timedelta
from typing import Literal, TypedDict

from django.db.models import Count, Q, Sum
from django.utils import timezone

from apps.practice.models import PracticeHistory
from apps.statistics.services import MS_PER_MINUTE

# Máximo de posições retornadas — suficiente para um ranking de topo sem
# paginação (escala do app não justifica a complexidade extra ainda).
LEADERBOARD_LIMIT = 50

Period = Literal["general", "weekly", "monthly"]

# "general" = todo o histórico; os demais são janelas móveis em dias
# corridos (UTC, mesmo fuso do resto do backend) — não mês/semana civil.
PERIOD_WINDOW_DAYS: dict[str, int | None] = {
    "general": None,
    "weekly": 7,
    "monthly": 30,
}


class LeaderboardEntry(TypedDict):
    position: int
    username: str
    accuracy: float
    cpm: float
    score: float


def get_leaderboard(speed_wpm: int, exercise_type: str, period: Period) -> list[LeaderboardEntry]:
    """Ranking dos usuários para o filtro dado, ordenado por pontuação desc.

    ``score = accuracy * 100 + cpm`` — soma a acurácia (0–100 pontos) ao CPM
    bruto; pontuação simples, não normalizada por WPM.
    """
    queryset = PracticeHistory.objects.filter(speed_wpm=speed_wpm, exercise_type=exercise_type)

    window_days = PERIOD_WINDOW_DAYS[period]
    if window_days is not None:
        queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=window_days))

    rows = queryset.values("user__username").annotate(
        seen=Count("id"),
        correct=Count("id", filter=Q(correct=True)),
        time=Sum("response_time"),
    )

    unranked: list[tuple[str, float, float, float]] = []
    for row in rows:
        seen: int = row["seen"]
        training_time: int = row["time"] or 0
        accuracy = row["correct"] / seen if seen else 0.0
        cpm = seen * MS_PER_MINUTE / training_time if training_time else 0.0
        unranked.append((row["user__username"], accuracy, cpm, accuracy * 100 + cpm))

    unranked.sort(key=lambda entry: entry[3], reverse=True)
    return [
        {
            "position": position,
            "username": username,
            "accuracy": accuracy,
            "cpm": cpm,
            "score": score,
        }
        for position, (username, accuracy, cpm, score) in enumerate(
            unranked[:LEADERBOARD_LIMIT], start=1
        )
    ]
