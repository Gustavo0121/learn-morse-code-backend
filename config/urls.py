"""Roteamento raiz da API.

As rotas dos demais apps (`/api/lessons/`, `/api/practice/` etc.) serão
registradas aqui nas fases seguintes.
"""

from django.contrib import admin
from django.http import HttpRequest, JsonResponse
from django.urls import include, path


def health(_request: HttpRequest) -> JsonResponse:
    """Endpoint de verificação usado por Docker healthcheck e smoke tests."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health, name="health"),
    path("api/", include("apps.accounts.urls")),
    path("api/", include("apps.morse.urls")),
    path("api/", include("apps.lessons.urls")),
    path("api/", include("apps.practice.urls")),
]
