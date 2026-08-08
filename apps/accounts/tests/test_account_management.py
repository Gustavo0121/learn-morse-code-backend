"""Testes da issue #27 — troca de senha e exclusão de conta."""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from apps.accounts.models import User
from apps.morse.models import UserMorseSettings
from apps.statistics.models import UserStatistics

pytestmark = pytest.mark.django_db

PASSWORD = "morse-Pr4ctice!"
NEW_PASSWORD = "outra-Pr4ctice!"


@pytest.fixture
def user() -> User:
    return User.objects.create_user(username="gu", email="gu@example.com", password=PASSWORD)


@pytest.fixture
def api(user: User) -> APIClient:
    """Cliente autenticado com login real (para ter refresh token em cookie)."""
    client = APIClient()
    login = client.post(
        reverse("auth-login"), {"username": "gu", "password": PASSWORD}, format="json"
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.json()['access']}")
    return client


# --------------------------------------------------------- change-password


def test_change_password_requires_authentication() -> None:
    response = APIClient().post(
        reverse("users-change-password"),
        {"current_password": PASSWORD, "new_password": NEW_PASSWORD},
        format="json",
    )

    assert response.status_code == 401


def test_change_password_updates_hash_and_logs_in_with_new_password(
    api: APIClient, user: User
) -> None:
    response = api.post(
        reverse("users-change-password"),
        {"current_password": PASSWORD, "new_password": NEW_PASSWORD},
        format="json",
    )

    assert response.status_code == 204
    user.refresh_from_db()
    assert user.check_password(NEW_PASSWORD)

    login = APIClient().post(
        reverse("auth-login"), {"username": "gu", "password": NEW_PASSWORD}, format="json"
    )
    assert login.status_code == 200


def test_change_password_rejects_wrong_current_password(api: APIClient, user: User) -> None:
    response = api.post(
        reverse("users-change-password"),
        {"current_password": "senha-errada", "new_password": NEW_PASSWORD},
        format="json",
    )

    assert response.status_code == 400
    assert "current_password" in response.json()
    user.refresh_from_db()
    assert user.check_password(PASSWORD)


def test_change_password_rejects_weak_new_password(api: APIClient, user: User) -> None:
    response = api.post(
        reverse("users-change-password"),
        {"current_password": PASSWORD, "new_password": "12345678"},
        format="json",
    )

    assert response.status_code == 400
    assert "new_password" in response.json()
    user.refresh_from_db()
    assert user.check_password(PASSWORD)


def test_change_password_invalidates_existing_refresh_tokens(api: APIClient, user: User) -> None:
    refresh_cookie = (
        APIClient()
        .post(reverse("auth-login"), {"username": "gu", "password": PASSWORD}, format="json")
        .cookies["refresh_token"]
        .value
    )

    response = api.post(
        reverse("users-change-password"),
        {"current_password": PASSWORD, "new_password": NEW_PASSWORD},
        format="json",
    )
    assert response.status_code == 204

    retry_client = APIClient()
    retry_client.cookies["refresh_token"] = refresh_cookie
    retry = retry_client.post(reverse("auth-refresh"), headers={"X-CSRF-Protection": "1"})

    assert retry.status_code == 401


def test_change_password_is_rate_limited(api: APIClient, user: User) -> None:
    for _ in range(10):  # rate "auth" = 10/min
        api.post(
            reverse("users-change-password"),
            {"current_password": "senha-errada", "new_password": NEW_PASSWORD},
            format="json",
        )

    response = api.post(
        reverse("users-change-password"),
        {"current_password": PASSWORD, "new_password": NEW_PASSWORD},
        format="json",
    )

    assert response.status_code == 429


# ------------------------------------------------------------ delete account


def test_delete_account_requires_authentication() -> None:
    response = APIClient().delete(
        reverse("users-profile"), {"current_password": PASSWORD}, format="json"
    )

    assert response.status_code == 401


def test_delete_account_rejects_wrong_current_password(api: APIClient, user: User) -> None:
    response = api.delete(
        reverse("users-profile"), {"current_password": "senha-errada"}, format="json"
    )

    assert response.status_code == 400
    assert "current_password" in response.json()
    assert User.objects.filter(pk=user.pk).exists()


def test_delete_account_removes_user_and_cascades_related_data(api: APIClient, user: User) -> None:
    # UserMorseSettings já existe por signal no cadastro (apps/morse);
    # UserStatistics só é criado após uma tentativa — cria direto aqui.
    assert UserMorseSettings.objects.filter(user_id=user.pk).exists()
    UserStatistics.objects.create(user=user)

    response = api.delete(reverse("users-profile"), {"current_password": PASSWORD}, format="json")

    assert response.status_code == 204
    assert not User.objects.filter(pk=user.pk).exists()
    assert not UserMorseSettings.objects.filter(user_id=user.pk).exists()
    assert not UserStatistics.objects.filter(user_id=user.pk).exists()


def test_delete_account_clears_refresh_cookie(api: APIClient, user: User) -> None:
    response = api.delete(reverse("users-profile"), {"current_password": PASSWORD}, format="json")

    assert response.cookies["refresh_token"].value == ""


def test_delete_account_blacklists_existing_refresh_tokens(api: APIClient, user: User) -> None:
    refresh_cookie = (
        APIClient()
        .post(reverse("auth-login"), {"username": "gu", "password": PASSWORD}, format="json")
        .cookies["refresh_token"]
        .value
    )

    response = api.delete(reverse("users-profile"), {"current_password": PASSWORD}, format="json")
    assert response.status_code == 204
    assert BlacklistedToken.objects.exists()

    retry_client = APIClient()
    retry_client.cookies["refresh_token"] = refresh_cookie
    retry = retry_client.post(reverse("auth-refresh"), headers={"X-CSRF-Protection": "1"})

    assert retry.status_code == 401


def test_delete_account_is_rate_limited(api: APIClient, user: User) -> None:
    for _ in range(10):  # rate "auth" = 10/min
        api.delete(reverse("users-profile"), {"current_password": "senha-errada"}, format="json")

    response = api.delete(
        reverse("users-profile"), {"current_password": "senha-errada"}, format="json"
    )

    assert response.status_code == 429
