"""Testes da Fase 5 — estatísticas agregadas."""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.practice.models import PracticeHistory
from apps.statistics.models import UserStatistics
from apps.statistics.services import recalculate_statistics

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


def record_attempt(user: User, *, correct: bool, response_time: int) -> PracticeHistory:
    return PracticeHistory.objects.create(
        user=user,
        exercise_type="key_capture",
        input_method="Space",
        question="!",
        expected_answer="-.-.--",
        user_answer="-.-.--" if correct else ".-.",
        correct=correct,
        response_time=response_time,
    )


# ---------------------------------------------------------------- agregação


def test_statistics_computed_from_simulated_history(user: User) -> None:
    # 3 acertos em 4 tentativas, 4000 ms de treino no total.
    for correct, response_time in [(True, 500), (True, 1500), (True, 1000), (False, 1000)]:
        record_attempt(user, correct=correct, response_time=response_time)

    statistics = UserStatistics.objects.get(user=user)
    assert statistics.characters_seen == 4
    assert statistics.characters_correct == 3
    assert statistics.accuracy == pytest.approx(0.75)
    assert statistics.training_time == 4000
    # 4 caracteres em 4000 ms -> 60 caracteres por minuto.
    assert statistics.average_speed == pytest.approx(60.0)


def test_statistics_updated_after_each_attempt(user: User) -> None:
    record_attempt(user, correct=True, response_time=1000)
    assert UserStatistics.objects.get(user=user).accuracy == pytest.approx(1.0)

    record_attempt(user, correct=False, response_time=1000)
    statistics = UserStatistics.objects.get(user=user)
    assert statistics.characters_seen == 2
    assert statistics.accuracy == pytest.approx(0.5)


def test_recalculate_with_empty_history_zeroes_everything(user: User) -> None:
    record_attempt(user, correct=True, response_time=1000)
    PracticeHistory.objects.filter(user=user).delete()

    statistics = recalculate_statistics(user)

    assert statistics.characters_seen == 0
    assert statistics.characters_correct == 0
    assert statistics.accuracy == 0.0
    assert statistics.average_speed == 0.0
    assert statistics.training_time == 0


def test_statistics_created_via_practice_endpoint(api: APIClient, user: User) -> None:
    # Fluxo real: o POST de prática dispara o recálculo do agregado.
    response = api.post(
        reverse("practice-history"),
        {
            "exercise_type": "key_capture",
            "input_method": "Space",
            "question": "!",
            "expected_answer": "-.-.--",
            "press_durations": [200, 50, 200, 50, 200, 200],
            "response_time": 850,
        },
        format="json",
    )

    assert response.status_code == 201
    statistics = UserStatistics.objects.get(user=user)
    assert statistics.characters_seen == 1
    assert statistics.characters_correct == 1
    assert statistics.training_time == 850


# ------------------------------------------------------------------ endpoint


def test_get_statistics_requires_authentication() -> None:
    response = APIClient().get(reverse("users-statistics"))

    assert response.status_code == 401


def test_get_statistics_returns_zeroed_record_without_history(api: APIClient) -> None:
    response = api.get(reverse("users-statistics"))

    assert response.status_code == 200
    body = response.json()
    assert body["characters_seen"] == 0
    assert body["accuracy"] == 0.0
    assert body["average_speed"] == 0.0
    assert body["training_time"] == 0
    assert "updated_at" in body


def test_get_statistics_returns_own_aggregate_only(api: APIClient, user: User) -> None:
    other = User.objects.create_user(username="outro", email="outro@example.com", password=PASSWORD)
    record_attempt(other, correct=True, response_time=1000)
    record_attempt(user, correct=False, response_time=2000)

    body = api.get(reverse("users-statistics")).json()

    assert body["characters_seen"] == 1
    assert body["characters_correct"] == 0
    assert body["training_time"] == 2000


def test_client_cannot_write_statistics(api: APIClient, user: User) -> None:
    record_attempt(user, correct=False, response_time=1000)

    for method in (api.post, api.put, api.patch):
        response = method(reverse("users-statistics"), {"accuracy": 1.0, "characters_correct": 999})
        assert response.status_code == 405

    statistics = UserStatistics.objects.get(user=user)
    assert statistics.accuracy == 0.0
    assert statistics.characters_correct == 0
