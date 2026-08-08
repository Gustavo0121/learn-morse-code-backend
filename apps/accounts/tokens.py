"""Helpers para invalidar refresh tokens emitidos (blacklist)."""

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from .models import User


def blacklist_outstanding_tokens(user: User) -> None:
    """Invalida todos os refresh tokens ainda válidos do usuário.

    Usado na troca de senha (sessões antigas não devem sobreviver à troca) e
    na exclusão de conta — chamar antes de ``user.delete()``, já que o FK de
    ``OutstandingToken`` para o usuário vira nulo depois da exclusão.
    """
    tokens = OutstandingToken.objects.filter(user=user, blacklistedtoken__isnull=True)
    BlacklistedToken.objects.bulk_create(BlacklistedToken(token=token) for token in tokens)
