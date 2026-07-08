"""Serializers do app lessons."""

from rest_framework import serializers

from .models import Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "title", "description", "difficulty", "order", "created_at")
        read_only_fields = fields
