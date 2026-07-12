"""Testes da Fase 1 — registro, login, refresh via cookie, CSRF e logout."""

import pytest
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User

pytestmark = pytest.mark.django_db

PASSWORD = "morse-Pr4ctice!"
CSRF_HEADER = {"X-CSRF-Protection": "1"}
COOKIE = "refresh_token"


@pytest.fixture
def api() -> APIClient:
    return APIClient()


@pytest.fixture
def user() -> User:
    return User.objects.create_user(username="gu", email="gu@example.com", password=PASSWORD)


def login(api: APIClient, username: str = "gu", password: str = PASSWORD):
    return api.post(
        reverse("auth-login"), {"username": username, "password": password}, format="json"
    )


# ---------------------------------------------------------------- register


def test_register_creates_user_with_hashed_password(api: APIClient) -> None:
    response = api.post(
        reverse("auth-register"),
        {"username": "novo", "email": "novo@example.com", "password": PASSWORD},
        format="json",
    )

    assert response.status_code == 201
    assert "password" not in response.json()

    created = User.objects.get(username="novo")
    assert created.email == "novo@example.com"
    assert created.password != PASSWORD  # armazenado como hash
    assert created.check_password(PASSWORD)


def test_register_rejects_duplicate_email(api: APIClient, user: User) -> None:
    response = api.post(
        reverse("auth-register"),
        {"username": "outro", "email": user.email, "password": PASSWORD},
        format="json",
    )

    assert response.status_code == 400
    assert "email" in response.json()


def test_register_rejects_weak_password(api: APIClient) -> None:
    response = api.post(
        reverse("auth-register"),
        {"username": "novo", "email": "novo@example.com", "password": "12345678"},
        format="json",
    )

    assert response.status_code == 400
    assert not User.objects.filter(username="novo").exists()


# ------------------------------------------------------------------- login


def test_login_returns_access_in_body_and_refresh_in_cookie(api: APIClient, user: User) -> None:
    response = login(api)

    assert response.status_code == 200
    body = response.json()
    assert "access" in body
    assert "refresh" not in body  # refresh nunca vai no corpo

    cookie = response.cookies[COOKIE]
    assert cookie.value
    assert cookie["httponly"]
    assert cookie["samesite"] == "Strict"
    assert cookie["path"] == "/api/auth"


@override_settings(DEBUG=False)
def test_refresh_cookie_is_secure_outside_debug(api: APIClient, user: User) -> None:
    response = login(api)

    assert response.cookies[COOKIE]["secure"]


def test_login_with_wrong_password_returns_401(api: APIClient, user: User) -> None:
    response = login(api, password="senha-errada")

    assert response.status_code == 401
    assert COOKIE not in response.cookies


def test_login_is_rate_limited(api: APIClient, user: User) -> None:
    for _ in range(10):  # rate "auth" = 10/min
        login(api, password="senha-errada")

    response = login(api)

    assert response.status_code == 429


# ----------------------------------------------------------------- refresh


def test_refresh_requires_csrf_header(api: APIClient, user: User) -> None:
    login(api)

    response = api.post(reverse("auth-refresh"))

    assert response.status_code == 403


def test_refresh_without_cookie_returns_401(api: APIClient) -> None:
    response = api.post(reverse("auth-refresh"), headers=CSRF_HEADER)

    assert response.status_code == 401


def test_refresh_returns_new_access_and_rotates_cookie(api: APIClient, user: User) -> None:
    old_refresh = login(api).cookies[COOKIE].value

    response = api.post(reverse("auth-refresh"), headers=CSRF_HEADER)

    assert response.status_code == 200
    body = response.json()
    assert "access" in body
    assert "refresh" not in body

    new_cookie = response.cookies[COOKIE]
    assert new_cookie["httponly"]
    assert new_cookie.value != old_refresh  # rotação


def test_rotated_refresh_token_is_blacklisted(api: APIClient, user: User) -> None:
    old_refresh = login(api).cookies[COOKIE].value
    api.post(reverse("auth-refresh"), headers=CSRF_HEADER)  # rotaciona

    api.cookies[COOKIE] = old_refresh  # tenta reusar o token antigo
    response = api.post(reverse("auth-refresh"), headers=CSRF_HEADER)

    assert response.status_code == 401


# ------------------------------------------------------------------ logout


def test_logout_requires_csrf_header(api: APIClient, user: User) -> None:
    login(api)

    response = api.post(reverse("auth-logout"))

    assert response.status_code == 403


def test_logout_clears_cookie_and_blacklists_token(api: APIClient, user: User) -> None:
    refresh = login(api).cookies[COOKIE].value

    response = api.post(reverse("auth-logout"), headers=CSRF_HEADER)

    assert response.status_code == 204
    assert response.cookies[COOKIE].value == ""  # cookie expirado

    api.cookies[COOKIE] = refresh  # token antigo não pode mais ser usado
    retry = api.post(reverse("auth-refresh"), headers=CSRF_HEADER)
    assert retry.status_code == 401


def test_logout_without_cookie_is_idempotent(api: APIClient) -> None:
    response = api.post(reverse("auth-logout"), headers=CSRF_HEADER)

    assert response.status_code == 204
