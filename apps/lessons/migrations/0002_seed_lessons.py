"""Seed das lições iniciais (progressão Nível 1 a 4)."""

from django.db import migrations

INITIAL_LESSONS = [
    {
        "order": 1,
        "difficulty": 1,
        "title": "Introdução — Letras básicas",
        "description": (
            "Primeiros passos no Código Morse: pontos, traços e as letras "
            "mais frequentes (E, T, A, N, I, M)."
        ),
    },
    {
        "order": 2,
        "difficulty": 2,
        "title": "Números",
        "description": "Os dígitos de 0 a 9 e seus padrões regulares de cinco sinais.",
    },
    {
        "order": 3,
        "difficulty": 3,
        "title": "Palavras",
        "description": "Combinando letras e números para formar palavras completas.",
    },
    {
        "order": 4,
        "difficulty": 4,
        "title": "Frases",
        "description": "Frases inteiras, espaçamento entre palavras e ritmo de transmissão.",
    },
]


def seed_lessons(apps, _schema_editor):
    lesson = apps.get_model("lessons", "Lesson")
    for data in INITIAL_LESSONS:
        lesson.objects.get_or_create(order=data["order"], defaults=data)


def unseed_lessons(apps, _schema_editor):
    lesson = apps.get_model("lessons", "Lesson")
    lesson.objects.filter(order__in=[data["order"] for data in INITIAL_LESSONS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("lessons", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_lessons, unseed_lessons),
    ]
