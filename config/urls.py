"""Roteamento raiz da API.

As rotas de cada app (`/api/auth/`, `/api/users/`, `/api/lessons/`,
`/api/practice/` etc.) serão registradas aqui nas fases seguintes.
"""

from django.contrib import admin
from django.http import HttpRequest, JsonResponse
from django.urls import path


def health(_request: HttpRequest) -> JsonResponse:
    """Endpoint de verificação usado por Docker healthcheck e smoke tests."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health, name="health"),
]
