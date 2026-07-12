"""Modelos do app practice — registro de tentativas de exercício (Fase 4)."""

from django.conf import settings
from django.db import models


class PracticeHistory(models.Model):
    """Registro consolidado de uma tentativa de exercício.

    Modelo único para todos os tipos de exercício (captura por tecla,
    múltipla escolha, escuta). ``correct`` é sempre calculado no backend
    comparando ``expected_answer`` com ``user_answer`` — nunca aceito do
    cliente.
    """

    class ExerciseType(models.TextChoices):
        KEY_CAPTURE = "key_capture"
        MULTIPLE_CHOICE = "multiple_choice"
        LISTENING = "listening"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="practice_history",
    )
    exercise_type = models.CharField(max_length=32, choices=ExerciseType.choices)
    # Tecla usada na captura — só se aplica a exercise_type = "key_capture",
    # por isso nullable (requisito 5.3).
    input_method = models.CharField(max_length=32, null=True, blank=True)  # noqa: DJ001
    question = models.CharField(max_length=255)
    expected_answer = models.CharField(max_length=255)
    user_answer = models.CharField(max_length=255)
    correct = models.BooleanField()
    response_time = models.PositiveIntegerField()  # milissegundos
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "practice histories"
        indexes = [
            # Consultas de histórico e agregação de estatísticas (Fase 5)
            # filtram por usuário e período.
            models.Index(fields=["user", "created_at"], name="practice_user_created_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.exercise_type} de {self.user} em {self.created_at:%Y-%m-%d %H:%M}"
