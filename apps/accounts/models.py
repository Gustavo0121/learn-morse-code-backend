"""Modelos do app accounts."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User Model do projeto.

    Usa o campo padrão ``password`` do Django (armazenado como hash — PBKDF2).
    ``created_at``/``updated_at`` complementam o ``date_joined`` herdado, e o
    ``email`` recebe restrição de unicidade (o padrão do Django permite
    duplicados).
    """

    email = models.EmailField("email address", unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.username
