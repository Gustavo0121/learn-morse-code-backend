"""Registro dos modelos do app morse no Django admin.

AllowedKey é administrada por aqui: adicionar/desativar teclas permitidas
não exige deploy.
"""

from django.contrib import admin

from .models import AllowedKey, MorseCharacter, UserMorseSettings


@admin.register(MorseCharacter)
class MorseCharacterAdmin(admin.ModelAdmin):
    list_display = ("character", "code", "type")
    list_filter = ("type",)
    search_fields = ("character",)


@admin.register(AllowedKey)
class AllowedKeyAdmin(admin.ModelAdmin):
    list_display = ("code", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("code",)


@admin.register(UserMorseSettings)
class UserMorseSettingsAdmin(admin.ModelAdmin):
    list_display = ("user", "speed_wpm", "frequency", "volume", "wave_type", "input_key")
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("user__username",)
