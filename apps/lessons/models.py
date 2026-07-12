"""Modelos do app lessons — conteúdo educacional."""

from django.db import models


class Lesson(models.Model):
    """Lição da trilha de aprendizado.

    Escrita restrita ao Django admin; a API expõe somente leitura. ``order``
    define a posição na trilha (único, para a progressão ser determinística).
    """

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    difficulty = models.PositiveSmallIntegerField()
    order = models.PositiveIntegerField(unique=True)
    # Conteúdo da lição: caracteres usados no treino guiado do frontend.
    characters = models.ManyToManyField(
        "morse.MorseCharacter",
        blank=True,
        related_name="lessons",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("order",)

    def __str__(self) -> str:
        return f"{self.order}. {self.title}"
