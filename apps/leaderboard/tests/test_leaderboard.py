"""Testes do app leaderboard."""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.practice.models import PracticeHistory

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


def record_attempt(
    username: str,
    *,
    correct: bool,
    response_time: int,
    speed_wpm: int = 20,
    exercise_type: str = "key_capture",
    created_at: object = None,
) -> PracticeHistory:
    owner, _created = User.objects.get_or_create(
        username=username, defaults={"email": f"{username}@example.com"}
    )
    history = PracticeHistory.objects.create(
        user=owner,
        exercise_type=exercise_type,
        input_method="Space" if exercise_type == "key_capture" else None,
        question="!",
        expected_answer="-.-.--",
        user_answer="-.-.--" if correct else ".-.",
        correct=correct,
        response_time=response_time,
        speed_wpm=speed_wpm,
    )
    if created_at is not None:
        PracticeHistory.objects.filter(pk=history.pk).update(created_at=created_at)
    return history


def get_leaderboard(
    api: APIClient,
    *,
    speed_wpm: int = 20,
    exercise_type: str = "key_capture",
    **overrides: str | int,
):
    params: dict[str, str | int] = {
        "speed_wpm": speed_wpm,
        "exercise_type": exercise_type,
        **overrides,
    }
    return api.get(reverse("leaderboard"), params)


# --------------------------------------------------------------- autenticação


def test_leaderboard_requires_authentication() -> None:
    response = APIClient().get(
        reverse("leaderboard"), {"speed_wpm": "20", "exercise_type": "key_capture"}
    )

    assert response.status_code == 401


# -------------------------------------------------------------------- filtro


def test_isolates_by_speed_wpm(api: APIClient) -> None:
    record_attempt("alice", correct=True, response_time=1000, speed_wpm=20)
    record_attempt("bob", correct=True, response_time=1000, speed_wpm=25)

    body = get_leaderboard(api, speed_wpm=20).json()

    assert [entry["username"] for entry in body] == ["alice"]


def test_isolates_by_exercise_type(api: APIClient) -> None:
    record_attempt("alice", correct=True, response_time=1000, exercise_type="key_capture")
    record_attempt("bob", correct=True, response_time=1000, exercise_type="listening")

    body = get_leaderboard(api, exercise_type="key_capture").json()

    assert [entry["username"] for entry in body] == ["alice"]


def test_rejects_speed_wpm_outside_enum(api: APIClient) -> None:
    response = get_leaderboard(api, speed_wpm=999)

    assert response.status_code == 400
    assert "speed_wpm" in response.json()


def test_rejects_unknown_exercise_type(api: APIClient) -> None:
    response = get_leaderboard(api, exercise_type="unknown")

    assert response.status_code == 400
    assert "exercise_type" in response.json()


def test_rejects_unknown_period(api: APIClient) -> None:
    response = get_leaderboard(api, period="yearly")

    assert response.status_code == 400
    assert "period" in response.json()


def test_empty_filter_returns_empty_list(api: APIClient) -> None:
    body = get_leaderboard(api).json()

    assert body == []


# ------------------------------------------------------------------- período


def test_period_general_includes_old_attempts(api: APIClient) -> None:
    old = timezone.now() - timedelta(days=90)
    record_attempt("alice", correct=True, response_time=1000, created_at=old)

    body = get_leaderboard(api, period="general").json()

    assert [entry["username"] for entry in body] == ["alice"]


def test_period_weekly_excludes_attempts_older_than_7_days(api: APIClient) -> None:
    record_attempt("alice", correct=True, response_time=1000)
    old = timezone.now() - timedelta(days=8)
    record_attempt("bob", correct=True, response_time=1000, created_at=old)

    body = get_leaderboard(api, period="weekly").json()

    assert [entry["username"] for entry in body] == ["alice"]


def test_period_monthly_excludes_attempts_older_than_30_days(api: APIClient) -> None:
    record_attempt("alice", correct=True, response_time=1000)
    old = timezone.now() - timedelta(days=31)
    record_attempt("bob", correct=True, response_time=1000, created_at=old)

    body = get_leaderboard(api, period="monthly").json()

    assert [entry["username"] for entry in body] == ["alice"]


# --------------------------------------------------------------- classificação


def test_ranks_by_score_descending(api: APIClient) -> None:
    # alice: 100% de acerto, 60 cpm -> score 160.
    record_attempt("alice", correct=True, response_time=1000)
    # bob: 0% de acerto, 60 cpm -> score 60.
    record_attempt("bob", correct=False, response_time=1000)

    body = get_leaderboard(api).json()

    assert [entry["username"] for entry in body] == ["alice", "bob"]
    assert body[0]["position"] == 1
    assert body[1]["position"] == 2
    assert body[0]["score"] > body[1]["score"]


def test_aggregates_multiple_attempts_per_user(api: APIClient) -> None:
    record_attempt("alice", correct=True, response_time=1000)
    record_attempt("alice", correct=False, response_time=1000)

    body = get_leaderboard(api).json()

    assert len(body) == 1
    assert body[0]["accuracy"] == pytest.approx(0.5)
