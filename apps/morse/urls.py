"""Rotas do app morse (montadas sob /api/ no urls raiz)."""

from django.urls import path

from .views import UserMorseSettingsView

urlpatterns = [
    path("users/morse-settings", UserMorseSettingsView.as_view(), name="users-morse-settings"),
]
