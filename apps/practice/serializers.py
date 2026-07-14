"""Serializers do app practice."""

from typing import Any

from rest_framework import serializers

from apps.morse.models import AllowedKey
from apps.morse.services import ensure_default_settings

from .models import TOUCH_INPUT_METHOD, PracticeHistory
from .services import allowed_press_limit_ms, code_from_press_durations

# Limite de sanidade para o tempo total de resposta (ms) — bloqueia payloads
# manipulados como {"response_time": 999999999}.
MAX_RESPONSE_TIME_MS = 5 * 60 * 1000


class PracticeHistorySerializer(serializers.ModelSerializer):
    """Registro e leitura de tentativas de exercício.

    Para ``key_capture`` o cliente pode enviar ``press_durations`` (duração
    de cada pressionamento, em ms): o backend valida cada duração contra o
    limite derivado do ``speed_wpm`` do usuário e refaz a classificação
    ponto/traço, derivando ``user_answer`` no servidor. ``correct`` é sempre
    calculado aqui, nunca aceito do cliente.
    """

    press_durations = serializers.ListField(
        child=serializers.FloatField(),
        write_only=True,
        required=False,
        allow_empty=False,
    )

    class Meta:
        model = PracticeHistory
        fields = (
            "id",
            "exercise_type",
            "input_method",
            "question",
            "expected_answer",
            "user_answer",
            "press_durations",
            "correct",
            "response_time",
            "created_at",
        )
        read_only_fields = ("id", "correct", "created_at")
        extra_kwargs = {
            # Derivado de press_durations quando o exercício é key_capture.
            "user_answer": {"required": False},
        }

    def validate_response_time(self, value: int) -> int:
        if not 0 < value <= MAX_RESPONSE_TIME_MS:
            raise serializers.ValidationError(
                f"Tempo de resposta deve estar entre 1 e {MAX_RESPONSE_TIME_MS} ms."
            )
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        exercise_type = attrs["exercise_type"]
        if exercise_type == PracticeHistory.ExerciseType.KEY_CAPTURE:
            self._validate_key_capture(attrs)
        else:
            self._validate_other_exercise(attrs)

        if "user_answer" not in attrs:
            raise serializers.ValidationError(
                {"user_answer": "Obrigatório quando press_durations não é enviado."}
            )

        attrs["correct"] = attrs["user_answer"] == attrs["expected_answer"]
        return attrs

    def _validate_key_capture(self, attrs: dict[str, Any]) -> None:
        input_method = attrs.get("input_method")
        if not input_method:
            raise serializers.ValidationError(
                {"input_method": "Obrigatório para exercícios key_capture."}
            )
        # "Touch" identifica captura por toque na tela (mobile) — não é uma
        # tecla, então é aceito fora da whitelist AllowedKey.
        if input_method != TOUCH_INPUT_METHOD and not (
            AllowedKey.objects.filter(code=input_method, is_active=True).exists()
        ):
            raise serializers.ValidationError(
                {"input_method": "Tecla não permitida. Consulte a lista de teclas válidas."}
            )

        durations = attrs.pop("press_durations", None)
        if durations is None:
            return

        speed_wpm = ensure_default_settings(self.context["request"].user).speed_wpm
        limit_ms = allowed_press_limit_ms(speed_wpm)
        if any(not 0 < duration < limit_ms for duration in durations):
            raise serializers.ValidationError(
                {
                    "press_durations": (
                        f"Cada duração deve estar entre 0 e {limit_ms:.0f} ms para {speed_wpm} WPM."
                    )
                }
            )
        attrs["user_answer"] = code_from_press_durations(durations, speed_wpm)

    def _validate_other_exercise(self, attrs: dict[str, Any]) -> None:
        if attrs.get("input_method"):
            raise serializers.ValidationError(
                {"input_method": "Só se aplica a exercícios key_capture."}
            )
        if attrs.pop("press_durations", None) is not None:
            raise serializers.ValidationError(
                {"press_durations": "Só se aplica a exercícios key_capture."}
            )
