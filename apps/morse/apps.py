from django.apps import AppConfig


class MorseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.morse"

    def ready(self) -> None:
        from . import signals  # noqa: F401 — registra os receivers
