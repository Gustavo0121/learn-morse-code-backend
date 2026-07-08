"""Permissões customizadas do app accounts."""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

CSRF_HEADER = "X-CSRF-Protection"


class RequireCSRFHeader(BasePermission):
    """Proteção CSRF para rotas que dependem do cookie de refresh.

    Exige um header customizado. Formulários cross-site não conseguem definir
    headers customizados, e em requisições fetch/XHR cross-origin o header
    dispara preflight CORS — portanto sua presença garante que a chamada veio
    do próprio frontend (same-origin ou origem explicitamente liberada).
    """

    message = f'Header "{CSRF_HEADER}: 1" é obrigatório nesta rota.'

    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.headers.get(CSRF_HEADER) == "1"
