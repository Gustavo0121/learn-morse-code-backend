"""Registro dos modelos do app practice no Django admin."""

from django.contrib import admin

from .models import PracticeHistory


@admin.register(PracticeHistory)
class PracticeHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "exercise_type", "correct", "response_time", "created_at")
    list_filter = ("exercise_type", "correct")
    search_fields = ("user__username",)
    readonly_fields = ("created_at",)
