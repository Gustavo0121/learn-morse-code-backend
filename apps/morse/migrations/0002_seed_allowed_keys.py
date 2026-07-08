"""Seed inicial da lista configurável de teclas permitidas."""

from django.db import migrations

INITIAL_KEYS = ["Space", "Enter", "KeyA", "KeyS", "KeyD"]


def seed_allowed_keys(apps, _schema_editor):
    allowed_key = apps.get_model("morse", "AllowedKey")
    for code in INITIAL_KEYS:
        allowed_key.objects.get_or_create(code=code)


def unseed_allowed_keys(apps, _schema_editor):
    allowed_key = apps.get_model("morse", "AllowedKey")
    allowed_key.objects.filter(code__in=INITIAL_KEYS).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("morse", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_allowed_keys, unseed_allowed_keys),
    ]
