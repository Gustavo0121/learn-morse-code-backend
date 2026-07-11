"""Serializers do app statistics."""

from rest_framework import serializers

from .models import UserStatistics


class UserStatisticsSerializer(serializers.ModelSerializer):
    """Leitura do agregado — todos os campos são somente leitura."""

    class Meta:
        model = UserStatistics
        fields = (
            "characters_seen",
            "characters_correct",
            "accuracy",
            "average_speed",
            "training_time",
            "updated_at",
        )
        read_only_fields = fields
