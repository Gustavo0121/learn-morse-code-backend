"""Rotas do app morse (montadas sob /api/ no urls raiz)."""

from django.urls import path

from .views import AllowedKeyListView, MorseCharacterListView, UserMorseSettingsView

urlpatterns = [
    path("users/morse-settings", UserMorseSettingsView.as_view(), name="users-morse-settings"),
    path(
        "morse-settings/allowed-keys",
        AllowedKeyListView.as_view(),
        name="morse-settings-allowed-keys",
    ),
    path("morse-characters", MorseCharacterListView.as_view(), name="morse-characters-list"),
]
