"""Rotas do app morse (montadas sob /api/ no urls raiz)."""

from django.urls import path

from .views import MorseCharacterListView, UserMorseSettingsView

urlpatterns = [
    path("users/morse-settings", UserMorseSettingsView.as_view(), name="users-morse-settings"),
    path("morse-characters", MorseCharacterListView.as_view(), name="morse-characters-list"),
]
