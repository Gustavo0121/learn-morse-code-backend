"""Views do app practice (Fase 4)."""

from typing import cast

from django.db.models import QuerySet
from rest_framework import generics
from rest_framework.serializers import BaseSerializer

from apps.accounts.models import User

from .models import PracticeHistory
from .serializers import PracticeHistorySerializer


class PracticeHistoryView(generics.ListCreateAPIView):
    """GET/POST /api/practice/history — sempre do usuário autenticado."""

    serializer_class = PracticeHistorySerializer

    def get_queryset(self) -> QuerySet[PracticeHistory]:
        return PracticeHistory.objects.filter(user=cast(User, self.request.user))

    def perform_create(self, serializer: BaseSerializer[PracticeHistory]) -> None:
        serializer.save(user=self.request.user)
