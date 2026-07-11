"""Registro dos modelos do app statistics no Django admin."""

from django.contrib import admin

from .models import UserStatistics


@admin.register(UserStatistics)
class UserStatisticsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "characters_seen",
        "characters_correct",
        "accuracy",
        "average_speed",
        "training_time",
        "updated_at",
    )
    search_fields = ("user__username",)
    # Agregado recalculado internamente — não editar à mão nem pelo admin.
    readonly_fields = (
        "user",
        "characters_seen",
        "characters_correct",
        "accuracy",
        "average_speed",
        "training_time",
        "updated_at",
    )
