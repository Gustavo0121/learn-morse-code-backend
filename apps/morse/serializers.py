"""Serializers do app morse."""

from rest_framework import serializers

from .models import AllowedKey, UserMorseSettings


class UserMorseSettingsSerializer(serializers.ModelSerializer):
    """Leitura e atualização das configurações de treino do usuário.

    Validações de domínio: ``speed_wpm`` e ``wave_type`` são restritos pelos
    choices do modelo; ``frequency`` e ``volume`` pelos validators de faixa;
    ``input_key`` é checado contra a tabela configurável ``AllowedKey``.
    """

    class Meta:
        model = UserMorseSettings
        fields = ("speed_wpm", "frequency", "volume", "wave_type", "input_key")

    def validate_input_key(self, value: str) -> str:
        if not AllowedKey.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError(
                "Tecla não permitida. Consulte a lista de teclas válidas."
            )
        return value
