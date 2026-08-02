"""Serializers do app leaderboard."""

from rest_framework import serializers

from apps.morse.models import UserMorseSettings
from apps.practice.models import PracticeHistory

PERIOD_CHOICES = ("general", "weekly", "monthly")


class LeaderboardQuerySerializer(serializers.Serializer):
    """Valida os filtros de ``GET /api/leaderboard``."""

    speed_wpm = serializers.ChoiceField(choices=UserMorseSettings.SpeedWpm.choices)
    exercise_type = serializers.ChoiceField(choices=PracticeHistory.ExerciseType.choices)
    period = serializers.ChoiceField(choices=PERIOD_CHOICES, default="general")


class LeaderboardEntrySerializer(serializers.Serializer):
    """Uma posição do ranking — somente leitura, computada em services.py."""

    position = serializers.IntegerField()
    username = serializers.CharField()
    accuracy = serializers.FloatField()
    cpm = serializers.FloatField()
    score = serializers.FloatField()
