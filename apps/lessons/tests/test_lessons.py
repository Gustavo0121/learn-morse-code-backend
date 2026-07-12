"""Testes da Fase 3 — lições."""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.lessons.models import Lesson

pytestmark = pytest.mark.django_db

PASSWORD = "morse-Pr4ctice!"


@pytest.fixture
def api() -> APIClient:
    user = User.objects.create_user(username="gu", email="gu@example.com", password=PASSWORD)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_list_requires_authentication() -> None:
    response = APIClient().get(reverse("lessons-list"))

    assert response.status_code == 401


def test_list_returns_seeded_lessons_ordered_by_order(api: APIClient) -> None:
    response = api.get(reverse("lessons-list"))

    assert response.status_code == 200
    lessons = response.json()
    assert len(lessons) == 4
    assert [lesson["order"] for lesson in lessons] == [1, 2, 3, 4]
    assert lessons[0]["title"] == "Introdução — Letras básicas"
    assert lessons[3]["title"] == "Frases"


def test_seeded_lessons_have_increasing_difficulty(api: APIClient) -> None:
    difficulties = [lesson["difficulty"] for lesson in api.get(reverse("lessons-list")).json()]

    assert difficulties == sorted(difficulties)


def test_list_respects_order_field_not_insertion_order(api: APIClient) -> None:
    Lesson.objects.create(title="Lição intermediária", difficulty=1, order=0)

    lessons = api.get(reverse("lessons-list")).json()

    assert lessons[0]["title"] == "Lição intermediária"


def test_detail_returns_lesson(api: APIClient) -> None:
    lesson = Lesson.objects.get(order=2)

    response = api.get(reverse("lessons-detail", args=[lesson.id]))

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Números"
    assert body["difficulty"] == 2


def test_lessons_embed_their_characters(api: APIClient) -> None:
    lesson = Lesson.objects.get(order=2)

    body = api.get(reverse("lessons-detail", args=[lesson.id])).json()

    characters = body["characters"]
    assert len(characters) == 10
    assert {item["type"] for item in characters} == {"number"}
    assert {"character", "code", "type", "id"} == set(characters[0].keys())


def test_seeded_lesson_one_has_basic_letters(api: APIClient) -> None:
    lesson = Lesson.objects.get(order=1)

    body = api.get(reverse("lessons-detail", args=[lesson.id])).json()

    assert sorted(item["character"] for item in body["characters"]) == [
        "A",
        "E",
        "I",
        "M",
        "N",
        "T",
    ]


def test_detail_unknown_id_returns_404(api: APIClient) -> None:
    response = api.get(reverse("lessons-detail", args=[99999]))

    assert response.status_code == 404


def test_write_is_not_exposed_via_api(api: APIClient) -> None:
    response = api.post(reverse("lessons-list"), {"title": "hack"}, format="json")

    assert response.status_code == 405  # somente leitura; escrita só via admin
