"""Testes da Fase 2 — configurações personalizadas de Morse."""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.morse.models import AllowedKey, UserMorseSettings

pytestmark = pytest.mark.django_db

PASSWORD = "morse-Pr4ctice!"

DEFAULTS = {
    "speed_wpm": 20,
    "frequency": 700,
    "volume": 0.8,
    "wave_type": "sine",
    "input_key": "Space",
}


@pytest.fixture
def user() -> User:
    return User.objects.create_user(username="gu", email="gu@example.com", password=PASSWORD)


@pytest.fixture
def api(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def put_settings(api: APIClient, **overrides: object):
    return api.put(reverse("users-morse-settings"), {**DEFAULTS, **overrides}, format="json")


# ------------------------------------------------------- criação automática


def test_settings_created_automatically_on_user_creation(user: User) -> None:
    settings = UserMorseSettings.objects.get(user=user)

    assert settings.input_key == "Space"
    assert settings.speed_wpm == 20


def test_settings_created_on_register_via_api() -> None:
    client = APIClient()
    response = client.post(
        reverse("auth-register"),
        {"username": "novo", "email": "novo@example.com", "password": PASSWORD},
        format="json",
    )

    assert response.status_code == 201
    assert UserMorseSettings.objects.filter(user__username="novo").exists()


# ------------------------------------------------------------------ leitura


def test_get_settings_requires_authentication() -> None:
    response = APIClient().get(reverse("users-morse-settings"))

    assert response.status_code == 401


def test_get_settings_returns_defaults(api: APIClient) -> None:
    response = api.get(reverse("users-morse-settings"))

    assert response.status_code == 200
    assert response.json() == DEFAULTS


def test_get_settings_creates_record_for_legacy_user(api: APIClient, user: User) -> None:
    # Usuários criados antes do signal (ex.: Fase 1) não têm o registro 1:1.
    UserMorseSettings.objects.filter(user=user).delete()

    response = api.get(reverse("users-morse-settings"))

    assert response.status_code == 200
    assert UserMorseSettings.objects.filter(user=user).exists()


# -------------------------------------------------------------- atualização


def test_put_settings_updates_and_persists(api: APIClient, user: User) -> None:
    response = put_settings(
        api, speed_wpm=30, frequency=1000, volume=0.5, wave_type="square", input_key="Enter"
    )

    assert response.status_code == 200

    settings = UserMorseSettings.objects.get(user=user)
    assert settings.speed_wpm == 30
    assert settings.frequency == 1000
    assert settings.volume == 0.5
    assert settings.wave_type == "square"
    assert settings.input_key == "Enter"


@pytest.mark.parametrize("speed_wpm", [-10, 0, 7, 25, 999999])
def test_put_rejects_speed_outside_enum(api: APIClient, speed_wpm: int) -> None:
    response = put_settings(api, speed_wpm=speed_wpm)

    assert response.status_code == 400
    assert "speed_wpm" in response.json()


@pytest.mark.parametrize("frequency", [-1, 0, 199, 2001, 999999])
def test_put_rejects_frequency_outside_range(api: APIClient, frequency: int) -> None:
    response = put_settings(api, frequency=frequency)

    assert response.status_code == 400
    assert "frequency" in response.json()


@pytest.mark.parametrize("volume", [-0.1, 1.1, 999])
def test_put_rejects_volume_outside_range(api: APIClient, volume: float) -> None:
    response = put_settings(api, volume=volume)

    assert response.status_code == 400
    assert "volume" in response.json()


def test_put_rejects_unknown_wave_type(api: APIClient) -> None:
    response = put_settings(api, wave_type="noise")

    assert response.status_code == 400
    assert "wave_type" in response.json()


@pytest.mark.parametrize("input_key", ["<script>", "CTRL+ALT+DEL", "rm -rf /", "KeyZ", ""])
def test_put_rejects_key_not_in_allowed_list(api: APIClient, input_key: str) -> None:
    response = put_settings(api, input_key=input_key)

    assert response.status_code == 400
    assert "input_key" in response.json()


def test_put_rejects_deactivated_key(api: APIClient) -> None:
    AllowedKey.objects.filter(code="Enter").update(is_active=False)

    response = put_settings(api, input_key="Enter")

    assert response.status_code == 400
    assert "input_key" in response.json()


def test_new_allowed_key_works_without_code_change(api: APIClient) -> None:
    # Lista configurável: adicionar uma tecla no banco basta para aceitá-la.
    AllowedKey.objects.create(code="KeyJ")

    response = put_settings(api, input_key="KeyJ")

    assert response.status_code == 200
