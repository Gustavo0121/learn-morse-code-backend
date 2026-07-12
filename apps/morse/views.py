"""Views do app morse (Fases 2–3)."""

from typing import cast

from rest_framework import generics

from apps.accounts.models import User

from .models import AllowedKey, MorseCharacter, UserMorseSettings
from .serializers import (
    AllowedKeySerializer,
    MorseCharacterSerializer,
    UserMorseSettingsSerializer,
)
from .services import ensure_default_settings


class UserMorseSettingsView(generics.RetrieveUpdateAPIView):
    """GET/PUT/PATCH /api/users/morse-settings — sempre do usuário autenticado."""

    serializer_class = UserMorseSettingsSerializer

    def get_object(self) -> UserMorseSettings:
        # Fallback para usuários criados antes do signal existir.
        return ensure_default_settings(cast(User, self.request.user))


class AllowedKeyListView(generics.ListAPIView):
    """GET /api/morse-settings/allowed-keys — whitelist de teclas de captura.

    Fonte única para o frontend construir o seletor de ``input_key``,
    garantindo que cliente e servidor validem contra a mesma lista.
    """

    queryset = AllowedKey.objects.filter(is_active=True)
    serializer_class = AllowedKeySerializer


class MorseCharacterListView(generics.ListAPIView):
    """GET /api/morse-characters — alfabeto Morse, somente leitura."""

    queryset = MorseCharacter.objects.all()
    serializer_class = MorseCharacterSerializer
