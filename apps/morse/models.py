"""Modelos do app morse — configurações personalizadas de treino."""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Faixa permitida para a frequência do tom (Hz): 400 = grave, 700 = médio,
# 1000 = agudo.
MIN_FREQUENCY_HZ = 200
MAX_FREQUENCY_HZ = 2000

DEFAULT_INPUT_KEY = "Space"


class AllowedKey(models.Model):
    """Tecla permitida para captura de Morse (``input_key``).

    Mantida como dado configurável no banco — expandir a lista de teclas não
    exige deploy. Desativar uma tecla (``is_active=False``) a remove das
    opções válidas sem apagar o histórico de quem a usava.
    """

    code = models.CharField(max_length=32, unique=True)  # ex.: "Space", "KeyA"
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("code",)

    def __str__(self) -> str:
        return self.code


class MorseCharacter(models.Model):
    """Caractere do alfabeto Morse (letra, número ou pontuação).

    Escrita restrita ao Django admin; a API expõe somente leitura.
    """

    class CharacterType(models.TextChoices):
        LETTER = "letter"
        NUMBER = "number"
        PUNCTUATION = "punctuation"

    character = models.CharField(max_length=8, unique=True)  # ex.: "A", "5", "?"
    code = models.CharField(max_length=16)  # ex.: ".-", "-.-.--"
    type = models.CharField(max_length=16, choices=CharacterType.choices)

    class Meta:
        ordering = ("type", "character")

    def __str__(self) -> str:
        return f"{self.character} -> {self.code}"


class UserMorseSettings(models.Model):
    """Configurações de treino do usuário (relação 1:1, criadas no cadastro)."""

    class WaveType(models.TextChoices):
        SINE = "sine"
        SQUARE = "square"
        TRIANGLE = "triangle"
        SAWTOOTH = "sawtooth"

    class SpeedWpm(models.IntegerChoices):
        WPM_5 = 5
        WPM_10 = 10
        WPM_15 = 15
        WPM_20 = 20
        WPM_30 = 30
        WPM_40 = 40
        WPM_60 = 60

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="morse_settings",
    )

    # Configuração sonora
    speed_wpm = models.PositiveSmallIntegerField(choices=SpeedWpm.choices, default=SpeedWpm.WPM_20)
    frequency = models.PositiveIntegerField(
        default=700,
        validators=[MinValueValidator(MIN_FREQUENCY_HZ), MaxValueValidator(MAX_FREQUENCY_HZ)],
    )
    volume = models.FloatField(
        default=0.8,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    wave_type = models.CharField(max_length=16, choices=WaveType.choices, default=WaveType.SINE)

    # Configuração de entrada — validada contra AllowedKey no serializer
    input_key = models.CharField(max_length=32, default=DEFAULT_INPUT_KEY)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "user morse settings"

    def __str__(self) -> str:
        return f"Morse settings de {self.user}"
