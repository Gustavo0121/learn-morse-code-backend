"""Roteamento raiz da API."""

from django.contrib import admin
from django.http import HttpRequest, JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health(_request: HttpRequest) -> JsonResponse:
    """Endpoint de verificação usado por Docker healthcheck e smoke tests."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health, name="health"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("api/", include("apps.accounts.urls")),
    path("api/", include("apps.morse.urls")),
    path("api/", include("apps.lessons.urls")),
    path("api/", include("apps.practice.urls")),
    path("api/", include("apps.statistics.urls")),
]
