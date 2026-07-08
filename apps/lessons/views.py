"""Views do app lessons (Fase 3) — somente leitura para o aluno."""

from rest_framework import generics

from .models import Lesson
from .serializers import LessonSerializer


class LessonListView(generics.ListAPIView):
    """GET /api/lessons — ordenadas pela posição na trilha (``order``)."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonDetailView(generics.RetrieveAPIView):
    """GET /api/lessons/{id}."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
