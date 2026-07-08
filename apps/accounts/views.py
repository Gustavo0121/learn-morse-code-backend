"""Views de autenticação e perfil (Fase 1).

Fluxo do refresh token (decisão conjunta com o frontend):

* ``POST /api/auth/login`` retorna o access token no corpo e grava o refresh
  token em cookie httpOnly/Secure/SameSite=Strict (nunca no corpo).
* ``POST /api/auth/refresh`` lê o refresh token do cookie (não do body),
  retorna um novo access token e rotaciona o cookie de refresh.
* ``POST /api/auth/logout`` coloca o refresh token na blacklist e limpa o
  cookie.
* As rotas que dependem do cookie exigem o header customizado de proteção
  CSRF (ver ``RequireCSRFHeader``).
"""

from collections.abc import Sequence
from typing import Any, cast

from django.conf import settings
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import BaseThrottle, ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .cookies import clear_refresh_cookie, set_refresh_cookie
from .models import User
from .permissions import RequireCSRFHeader
from .serializers import ProfileSerializer, RegisterSerializer


class AuthThrottleMixin:
    """Rate limiting por IP nas rotas de autenticação (anti brute force)."""

    throttle_classes: Sequence[type[BaseThrottle]] = (ScopedRateThrottle,)
    throttle_scope = "auth"


class RegisterView(AuthThrottleMixin, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = ()
    authentication_classes = ()


class LoginView(AuthThrottleMixin, TokenObtainPairView):
    """Autentica e move o refresh token do corpo para o cookie httpOnly."""

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        response = super().post(request, *args, **kwargs)
        set_refresh_cookie(response, response.data.pop("refresh"))
        return response


class RefreshView(AuthThrottleMixin, TokenRefreshView):
    """Renova o access token a partir do refresh token vindo do cookie."""

    permission_classes = (RequireCSRFHeader,)  # type: ignore[assignment]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        token = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE_NAME)
        if not token:
            raise InvalidToken("Cookie de refresh token ausente.")

        serializer = self.get_serializer(data={"refresh": token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(exc.args[0]) from exc

        data = dict(serializer.validated_data)
        new_refresh = data.pop("refresh", None)

        response = Response(data, status=status.HTTP_200_OK)
        if new_refresh:  # ROTATE_REFRESH_TOKENS: cookie substituído a cada uso
            set_refresh_cookie(response, new_refresh)
        return response


class LogoutView(AuthThrottleMixin, APIView):
    """Coloca o refresh token na blacklist e expira o cookie.

    Idempotente: cookie ausente/inválido não gera erro — o resultado final
    (usuário sem sessão de refresh válida) é o mesmo.
    """

    # Autentica pelo cookie de refresh, não pelo access token (que pode já
    # ter expirado no momento do logout).
    authentication_classes = ()
    permission_classes = (RequireCSRFHeader,)

    def post(self, request: Request) -> Response:
        token = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE_NAME)
        if token:
            try:
                # O stub de RefreshToken não aceita str, mas a API aceita.
                RefreshToken(token).blacklist()  # type: ignore[arg-type]
            except TokenError:
                pass

        response = Response(status=status.HTTP_204_NO_CONTENT)
        clear_refresh_cookie(response)
        return response


class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PUT/PATCH /api/users/profile — sempre do usuário autenticado."""

    serializer_class = ProfileSerializer

    def get_object(self) -> User:
        # IsAuthenticated (permissão default) garante que não é AnonymousUser.
        return cast(User, self.request.user)
