"""Testes da Fase 6 — segurança transversal (headers, CORS, HTTPS, throttling).

As validações de entrada por endpoint (payloads maliciosos em ``input_key``,
``press_durations``, ``speed_wpm`` etc.) são cobertas nos testes de cada app;
aqui ficam as garantias que atravessam o projeto inteiro.
"""

import importlib

import pytest
from django.conf import settings as django_settings
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.throttling import UserRateThrottle

import config.settings
from apps.accounts.models import User

FRONTEND_ORIGIN = "https://morse.example.com"
EVIL_ORIGIN = "https://evil.example.org"


# ---------------------------------------------------------------------------
# Headers de segurança
# ---------------------------------------------------------------------------


def test_csp_header_present_in_all_responses(client: Client) -> None:
    response = client.get(reverse("health"))

    assert response["Content-Security-Policy"] == django_settings.CONTENT_SECURITY_POLICY
    assert "default-src 'none'" in response["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in response["Content-Security-Policy"]


def test_nosniff_and_frame_deny_headers_present(client: Client) -> None:
    response = client.get(reverse("health"))

    assert response["X-Content-Type-Options"] == "nosniff"
    assert response["X-Frame-Options"] == "DENY"


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------


def test_cors_allows_configured_origin_with_credentials(client: Client, settings) -> None:
    settings.CORS_ALLOWED_ORIGINS = [FRONTEND_ORIGIN]

    response = client.get(reverse("health"), HTTP_ORIGIN=FRONTEND_ORIGIN)

    assert response["Access-Control-Allow-Origin"] == FRONTEND_ORIGIN
    assert response["Access-Control-Allow-Credentials"] == "true"


def test_cors_rejects_unknown_origin(client: Client, settings) -> None:
    settings.CORS_ALLOWED_ORIGINS = [FRONTEND_ORIGIN]

    response = client.get(reverse("health"), HTTP_ORIGIN=EVIL_ORIGIN)

    assert "Access-Control-Allow-Origin" not in response


def test_cors_preflight_accepts_csrf_protection_header(client: Client, settings) -> None:
    settings.CORS_ALLOWED_ORIGINS = [FRONTEND_ORIGIN]

    response = client.options(
        reverse("auth-refresh"),
        HTTP_ORIGIN=FRONTEND_ORIGIN,
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        HTTP_ACCESS_CONTROL_REQUEST_HEADERS="x-csrf-protection",
    )

    assert response.status_code == 200
    assert "x-csrf-protection" in response["Access-Control-Allow-Headers"]


# ---------------------------------------------------------------------------
# Hardening de produção (bloco `if not DEBUG` do settings)
# ---------------------------------------------------------------------------


def _reload_settings_module():
    return importlib.reload(config.settings)


def test_production_settings_enforce_https_and_hsts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEBUG", "False")
    try:
        module = _reload_settings_module()

        assert module.SECURE_SSL_REDIRECT is True
        assert module.SESSION_COOKIE_SECURE is True
        assert module.CSRF_COOKIE_SECURE is True
        assert module.SECURE_HSTS_SECONDS == 60 * 60 * 24 * 365
        assert module.SECURE_HSTS_INCLUDE_SUBDOMAINS is True
        assert module.SECURE_REFERRER_POLICY == "same-origin"
        # Browsable API (HTML) desligada em produção — API somente JSON.
        assert module.REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] == (
            "rest_framework.renderers.JSONRenderer",
        )
    finally:
        monkeypatch.undo()
        _reload_settings_module()


def test_production_proxy_ssl_header_is_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEBUG", "False")
    try:
        module = _reload_settings_module()
        assert not hasattr(module, "SECURE_PROXY_SSL_HEADER")

        monkeypatch.setenv("USE_X_FORWARDED_PROTO", "True")
        module = _reload_settings_module()
        assert module.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")
    finally:
        monkeypatch.undo()
        _reload_settings_module()


def test_debug_settings_do_not_force_ssl() -> None:
    # A suíte roda com DEBUG=True — o bloco de produção não pode vazar.
    assert not getattr(django_settings, "SECURE_SSL_REDIRECT", False)


# ---------------------------------------------------------------------------
# Throttling global
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_authenticated_endpoints_are_rate_limited(monkeypatch: pytest.MonkeyPatch) -> None:
    # THROTTLE_RATES é atributo de classe capturado no import do DRF, então o
    # override precisa ser na classe, não em settings.REST_FRAMEWORK.
    monkeypatch.setattr(UserRateThrottle, "THROTTLE_RATES", {"user": "3/min"})
    user = User.objects.create_user(
        username="gu", email="gu@example.com", password="morse-Pr4ctice!"
    )
    api = APIClient()
    api.force_authenticate(user=user)

    responses = [api.get(reverse("lessons-list")).status_code for _ in range(4)]

    assert responses[:3] == [200, 200, 200]
    assert responses[3] == 429
