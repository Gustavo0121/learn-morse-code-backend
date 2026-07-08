"""Testes da Fase 3 — caracteres Morse."""

import pytest
from django.db import IntegrityError
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.morse.models import MorseCharacter

pytestmark = pytest.mark.django_db

PASSWORD = "morse-Pr4ctice!"


@pytest.fixture
def api() -> APIClient:
    user = User.objects.create_user(username="gu", email="gu@example.com", password=PASSWORD)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_list_requires_authentication() -> None:
    response = APIClient().get(reverse("morse-characters-list"))

    assert response.status_code == 401


def test_seed_contains_full_alphabet(api: APIClient) -> None:
    characters = api.get(reverse("morse-characters-list")).json()

    by_type: dict[str, list[dict]] = {}
    for entry in characters:
        by_type.setdefault(entry["type"], []).append(entry)

    assert len(by_type["letter"]) == 26
    assert len(by_type["number"]) == 10
    assert len(by_type["punctuation"]) == 18


def test_seeded_codes_match_itu_standard(api: APIClient) -> None:
    characters = {
        entry["character"]: entry["code"]
        for entry in api.get(reverse("morse-characters-list")).json()
    }

    assert characters["A"] == ".-"
    assert characters["B"] == "-..."
    assert characters["C"] == "-.-."
    assert characters["0"] == "-----"
    assert characters["9"] == "----."
    assert characters["?"] == "..--.."


def test_codes_contain_only_dots_and_dashes() -> None:
    for character in MorseCharacter.objects.all():
        assert set(character.code) <= {".", "-"}, character


def test_character_uniqueness_is_enforced() -> None:
    with pytest.raises(IntegrityError):
        MorseCharacter.objects.create(character="A", code="....", type="letter")


def test_write_is_not_exposed_via_api(api: APIClient) -> None:
    response = api.post(
        reverse("morse-characters-list"),
        {"character": "Ω", "code": ".", "type": "letter"},
        format="json",
    )

    assert response.status_code == 405  # somente leitura; escrita só via admin
