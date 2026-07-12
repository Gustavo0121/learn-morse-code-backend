"""Relação lição↔caracteres + seed do conteúdo das lições iniciais.

O treino guiado do frontend usa ``characters`` para restringir os exercícios
ao conteúdo da lição.
"""

from django.db import migrations, models

# Conteúdo das lições seedadas (por ``order``). As letras da lição 1 são as
# mais frequentes, citadas na própria descrição da lição.
LESSON_1_LETTERS = ["E", "T", "A", "N", "I", "M"]


def assign_characters(apps, _schema_editor):
    lesson_model = apps.get_model("lessons", "Lesson")
    character_model = apps.get_model("morse", "MorseCharacter")

    def assign(order, queryset):
        lesson = lesson_model.objects.filter(order=order).first()
        if lesson is not None:
            lesson.characters.set(queryset)

    assign(1, character_model.objects.filter(character__in=LESSON_1_LETTERS))
    assign(2, character_model.objects.filter(type="number"))
    assign(3, character_model.objects.filter(type="letter"))
    assign(4, character_model.objects.all())


def unassign_characters(apps, _schema_editor):
    lesson_model = apps.get_model("lessons", "Lesson")
    for lesson in lesson_model.objects.filter(order__in=[1, 2, 3, 4]):
        lesson.characters.clear()


class Migration(migrations.Migration):
    dependencies = [
        ("lessons", "0002_seed_lessons"),
        ("morse", "0004_seed_morse_characters"),
    ]

    operations = [
        migrations.AddField(
            model_name="lesson",
            name="characters",
            field=models.ManyToManyField(
                blank=True,
                related_name="lessons",
                to="morse.morsecharacter",
            ),
        ),
        migrations.RunPython(assign_characters, unassign_characters),
    ]
