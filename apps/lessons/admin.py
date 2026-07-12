"""Registro dos modelos do app lessons no Django admin."""

from django.contrib import admin

from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "difficulty", "created_at")
    ordering = ("order",)
    search_fields = ("title",)
    filter_horizontal = ("characters",)
