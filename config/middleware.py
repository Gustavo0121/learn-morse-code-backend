"""Middlewares de segurança do projeto (Fase 6)."""

from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponseBase


class ContentSecurityPolicyMiddleware:
    """Adiciona o header Content-Security-Policy a todas as respostas.

    A política vem de ``settings.CONTENT_SECURITY_POLICY``. Django 5.x não
    tem suporte nativo a CSP; este middleware evita uma dependência externa
    para um header estático.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponseBase]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponseBase:
        response = self.get_response(request)
        policy = settings.CONTENT_SECURITY_POLICY
        if request.path.startswith(settings.CONTENT_SECURITY_POLICY_DOCS_PATH):
            policy = settings.CONTENT_SECURITY_POLICY_DOCS
        response.headers.setdefault("Content-Security-Policy", policy)
        return response
