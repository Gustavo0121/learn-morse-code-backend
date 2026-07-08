"""Testes da Fase 1 — perfil do usuário autenticado."""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User

pytestmark = pytest.mark.django_db

PASSWORD = "morse-Pr4ctice!"


@pytest.fixture
def user() -> User:
    return User.objects.create_user(username="gu", email="gu@example.com", password=PASSWORD)


@pytest.fixture
def api(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_profile_requires_authentication() -> None:
    response = APIClient().get(reverse("users-profile"))

    assert response.status_code == 401


def test_profile_accepts_jwt_access_token(user: User) -> None:
    client = APIClient()
    access = client.post(
        reverse("auth-login"), {"username": "gu", "password": PASSWORD}, format="json"
    ).json()["access"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    response = client.get(reverse("users-profile"))

    assert response.status_code == 200
    assert response.json()["username"] == "gu"


def test_get_profile_returns_own_data_without_password(api: APIClient, user: User) -> None:
    response = api.get(reverse("users-profile"))

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "gu"
    assert body["email"] == "gu@example.com"
    assert "created_at" in body
    assert "updated_at" in body
    assert "password" not in body


def test_put_profile_updates_username_and_email(api: APIClient, user: User) -> None:
    response = api.put(
        reverse("users-profile"),
        {"username": "gu2", "email": "gu2@example.com"},
        format="json",
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.username == "gu2"
    assert user.email == "gu2@example.com"


def test_put_profile_rejects_email_already_in_use(api: APIClient) -> None:
    User.objects.create_user(username="outra", email="outra@example.com", password=PASSWORD)

    response = api.put(
        reverse("users-profile"),
        {"username": "gu", "email": "outra@example.com"},
        format="json",
    )

    assert response.status_code == 400
    assert "email" in response.json()
