"""Testes da Fase 4 — registro de treino (practice)."""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.morse.models import UserMorseSettings
from apps.practice.models import PracticeHistory
from apps.practice.services import allowed_press_limit_ms, code_from_press_durations

pytestmark = pytest.mark.django_db

PASSWORD = "morse-Pr4ctice!"

# Payload de referência do documento de requisitos (5.3).
KEY_CAPTURE_PAYLOAD = {
    "exercise_type": "key_capture",
    "input_method": "Space",
    "question": "!",
    "expected_answer": "-.-.--",
    "user_answer": ".-.",
    "response_time": 850,
}


@pytest.fixture
def user() -> User:
    return User.objects.create_user(username="gu", email="gu@example.com", password=PASSWORD)


@pytest.fixture
def api(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def post_history(api: APIClient, **overrides: object):
    payload = {**KEY_CAPTURE_PAYLOAD, **overrides}
    payload = {key: value for key, value in payload.items() if value is not None}
    return api.post(reverse("practice-history"), payload, format="json")


def set_speed(user: User, speed_wpm: int) -> None:
    UserMorseSettings.objects.filter(user=user).update(speed_wpm=speed_wpm)


# -------------------------------------------------------------- autenticação


def test_history_requires_authentication() -> None:
    client = APIClient()

    assert client.get(reverse("practice-history")).status_code == 401
    assert client.post(reverse("practice-history"), KEY_CAPTURE_PAYLOAD).status_code == 401


# ------------------------------------------------------------------ registro


def test_post_records_attempt_and_computes_correct_false(api: APIClient, user: User) -> None:
    response = post_history(api)

    assert response.status_code == 201
    record = PracticeHistory.objects.get(user=user)
    assert record.exercise_type == "key_capture"
    assert record.input_method == "Space"
    assert record.user_answer == ".-."
    assert record.correct is False  # ".-." != "-.-.--"
    assert record.response_time == 850


def test_post_computes_correct_true_when_answers_match(api: APIClient, user: User) -> None:
    response = post_history(api, user_answer="-.-.--")

    assert response.status_code == 201
    assert PracticeHistory.objects.get(user=user).correct is True


def test_correct_from_client_is_ignored(api: APIClient, user: User) -> None:
    # `correct` é calculado no backend; o valor enviado nunca é aceito.
    response = post_history(api, correct=True)

    assert response.status_code == 201
    assert PracticeHistory.objects.get(user=user).correct is False


def test_non_key_capture_exercise_without_input_method(api: APIClient, user: User) -> None:
    response = post_history(
        api,
        exercise_type="multiple_choice",
        input_method=None,
        question="Qual o código de A?",
        expected_answer=".-",
        user_answer=".-",
    )

    assert response.status_code == 201
    record = PracticeHistory.objects.get(user=user)
    assert record.input_method is None
    assert record.correct is True


# ---------------------------------------- classificação ponto/traço no backend


def test_press_durations_derive_user_answer_on_server(api: APIClient, user: User) -> None:
    # 20 WPM (padrão): ponto = 60 ms, traço a partir de 120 ms.
    response = post_history(
        api,
        user_answer=None,
        press_durations=[200, 50, 200, 50, 200, 200],
    )

    assert response.status_code == 201
    record = PracticeHistory.objects.get(user=user)
    assert record.user_answer == "-.-.--"
    assert record.correct is True


def test_press_durations_override_user_answer_sent_by_client(api: APIClient, user: User) -> None:
    # Cliente não pode alegar um código diferente do que as durações produzem.
    response = post_history(api, user_answer="-.-.--", press_durations=[50, 50])

    assert response.status_code == 201
    record = PracticeHistory.objects.get(user=user)
    assert record.user_answer == ".."
    assert record.correct is False


def test_classification_follows_configured_speed() -> None:
    # 400 ms é ponto a 5 WPM (ponto nominal = 240 ms, traço >= 480 ms)...
    assert code_from_press_durations([400], speed_wpm=5) == "."
    # ...e traço a 20 WPM (ponto nominal = 60 ms, traço >= 120 ms).
    assert code_from_press_durations([400], speed_wpm=20) == "-"


# ------------------------------------- validação server-side das durações


@pytest.mark.parametrize("duration", [0, -50, 999999999])
def test_rejects_press_duration_outside_limits(api: APIClient, duration: float) -> None:
    response = post_history(api, user_answer=None, press_durations=[duration])

    assert response.status_code == 400
    assert "press_durations" in response.json()


def test_allowed_limit_scales_with_speed_wpm() -> None:
    # Limite dinâmico: quanto maior o WPM, menor a duração máxima aceita.
    assert allowed_press_limit_ms(5) > allowed_press_limit_ms(20) > allowed_press_limit_ms(60)


def test_duration_valid_at_low_speed_rejected_at_high_speed(api: APIClient, user: User) -> None:
    set_speed(user, 5)
    assert post_history(api, user_answer=None, press_durations=[400]).status_code == 201

    set_speed(user, 60)
    response = post_history(api, user_answer=None, press_durations=[400])
    assert response.status_code == 400
    assert "press_durations" in response.json()


# ------------------------------------------------------- validações de campo


@pytest.mark.parametrize("input_method", ["<script>", "CTRL+ALT+DEL", "rm -rf /", "KeyZ", ""])
def test_rejects_input_method_not_in_allowed_list(api: APIClient, input_method: str) -> None:
    response = post_history(api, input_method=input_method)

    assert response.status_code == 400
    assert "input_method" in response.json()


def test_accepts_touch_input_method_outside_allowed_keys(api: APIClient, user: User) -> None:
    """Captura por toque (mobile) usa o literal "Touch", que não é tecla."""
    response = post_history(api, input_method="Touch", press_durations=[100, 100], user_answer=None)

    assert response.status_code == 201
    record = PracticeHistory.objects.get(user=user)
    assert record.input_method == "Touch"
    assert record.user_answer == ".."


@pytest.mark.parametrize("input_method", ["touch", "TOUCH"])
def test_touch_input_method_is_case_sensitive(api: APIClient, input_method: str) -> None:
    response = post_history(api, input_method=input_method)

    assert response.status_code == 400
    assert "input_method" in response.json()


def test_key_capture_requires_input_method(api: APIClient) -> None:
    response = post_history(api, input_method=None)

    assert response.status_code == 400
    assert "input_method" in response.json()


def test_non_key_capture_rejects_input_method(api: APIClient) -> None:
    response = post_history(api, exercise_type="multiple_choice", input_method="Space")

    assert response.status_code == 400
    assert "input_method" in response.json()


def test_non_key_capture_rejects_press_durations(api: APIClient) -> None:
    response = post_history(
        api, exercise_type="multiple_choice", input_method=None, press_durations=[50]
    )

    assert response.status_code == 400
    assert "press_durations" in response.json()


def test_rejects_unknown_exercise_type(api: APIClient) -> None:
    response = post_history(api, exercise_type="hack")

    assert response.status_code == 400
    assert "exercise_type" in response.json()


def test_requires_user_answer_when_no_press_durations(api: APIClient) -> None:
    response = post_history(api, user_answer=None)

    assert response.status_code == 400
    assert "user_answer" in response.json()


@pytest.mark.parametrize("response_time", [0, -1, 999999999])
def test_rejects_response_time_outside_limits(api: APIClient, response_time: int) -> None:
    response = post_history(api, response_time=response_time)

    assert response.status_code == 400
    assert "response_time" in response.json()


# ------------------------------------------------------------------- leitura


def test_get_returns_only_own_history_most_recent_first(api: APIClient, user: User) -> None:
    other = User.objects.create_user(username="outro", email="outro@example.com", password=PASSWORD)
    PracticeHistory.objects.create(
        user=other,
        exercise_type="listening",
        question="sos",
        expected_answer="sos",
        user_answer="sos",
        correct=True,
        response_time=100,
    )
    post_history(api)
    post_history(api, user_answer="-.-.--")

    response = api.get(reverse("practice-history"))

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert [item["correct"] for item in body] == [True, False]  # mais recente primeiro
    assert all("press_durations" not in item for item in body)  # write-only
