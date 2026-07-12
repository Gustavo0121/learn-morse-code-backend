"""Serializers do app lessons."""

from rest_framework import serializers

from apps.morse.models import MorseCharacter

from .models import Lesson


class LessonCharacterSerializer(serializers.ModelSerializer):
    """Caractere embutido na lição — mesmo formato de GET /api/morse-characters."""

    class Meta:
        model = MorseCharacter
        fields = ("id", "character", "code", "type")
        read_only_fields = fields


class LessonSerializer(serializers.ModelSerializer):
    characters = LessonCharacterSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = ("id", "title", "description", "difficulty", "order", "characters", "created_at")
        read_only_fields = fields
