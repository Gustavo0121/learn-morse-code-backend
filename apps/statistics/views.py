"""Views do app statistics (Fase 5)."""

from typing import cast

from rest_framework import generics

from apps.accounts.models import User

from .models import UserStatistics
from .serializers import UserStatisticsSerializer
from .services import ensure_statistics


class UserStatisticsView(generics.RetrieveAPIView):
    """GET /api/users/statistics — agregado do usuário autenticado, somente leitura."""

    serializer_class = UserStatisticsSerializer

    def get_object(self) -> UserStatistics:
        # Usuários sem histórico ainda não têm o registro — retorna zerado.
        return ensure_statistics(cast(User, self.request.user))
