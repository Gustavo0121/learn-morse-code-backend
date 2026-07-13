"""Testes da Fase 8 — documentação OpenAPI (/api/schema e /api/docs)."""

from django.conf import settings as django_settings
from django.test import Client
from django.urls import reverse


def test_schema_is_public_and_lists_all_endpoints(client: Client) -> None:
    response = client.get(reverse("schema"))

    assert response.status_code == 200
    schema = response.content.decode()
    for endpoint in (
        "/api/auth/login",
        "/api/auth/refresh",
        "/api/users/morse-settings",
        "/api/lessons",
        "/api/morse-characters",
        "/api/practice/history",
        "/api/users/statistics",
    ):
        assert endpoint in schema


def test_swagger_ui_page_renders_with_local_assets(client: Client) -> None:
    response = client.get(reverse("docs"))

    assert response.status_code == 200
    html = response.content.decode()
    # Assets do sidecar (self-hosted) — nenhuma referência a CDN externo.
    assert "/static/drf_spectacular_sidecar/" in html
    assert "cdn.jsdelivr.net" not in html


def test_docs_page_gets_relaxed_csp_but_other_routes_keep_strict(client: Client) -> None:
    docs_csp = client.get(reverse("docs"))["Content-Security-Policy"]
    api_csp = client.get(reverse("health"))["Content-Security-Policy"]

    assert "script-src 'self' 'unsafe-inline'" in docs_csp
    assert "script-src 'self';" in api_csp
    assert api_csp == django_settings.CONTENT_SECURITY_POLICY
