"""Registro do User customizado no Django admin."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_staff", "created_at")
    readonly_fields = ("created_at", "updated_at")
