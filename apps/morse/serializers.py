"""Serializers do app morse."""

from rest_framework import serializers

from .models import AllowedKey, MorseCharacter, UserMorseSettings


class AllowedKeySerializer(serializers.ModelSerializer):
    """Tecla válida para ``input_key`` — consumida pelo seletor do frontend."""

    class Meta:
        model = AllowedKey
        fields = ("code",)
        read_only_fields = fields


class MorseCharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MorseCharacter
        fields = ("id", "character", "code", "type")
        read_only_fields = fields


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
