"""Helpers para o cookie httpOnly que transporta o refresh token."""

from datetime import timedelta
from typing import cast

from django.conf import settings
from rest_framework.response import Response


def set_refresh_cookie(response: Response, token: str) -> None:
    """Grava o refresh token como cookie httpOnly/Secure/SameSite=Strict.

    ``secure`` é desligado apenas em DEBUG (dev local sem HTTPS); em produção
    o cookie só trafega por HTTPS.
    """
    response.set_cookie(
        settings.REFRESH_TOKEN_COOKIE_NAME,
        token,
        max_age=int(cast(timedelta, settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]).total_seconds()),
        path=settings.REFRESH_TOKEN_COOKIE_PATH,
        secure=not settings.DEBUG,
        httponly=True,
        samesite="Strict",
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        settings.REFRESH_TOKEN_COOKIE_NAME,
        path=settings.REFRESH_TOKEN_COOKIE_PATH,
        samesite="Strict",
    )
