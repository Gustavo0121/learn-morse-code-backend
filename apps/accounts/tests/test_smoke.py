"""Smoke tests da Fase 0: garantem que o projeto sobe e responde."""

from django.test import Client
from django.urls import reverse


def test_health_endpoint_returns_ok() -> None:
    response = Client().get(reverse("health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
