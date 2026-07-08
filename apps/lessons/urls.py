"""Rotas do app lessons (montadas sob /api/ no urls raiz)."""

from django.urls import path

from .views import LessonDetailView, LessonListView

urlpatterns = [
    path("lessons", LessonListView.as_view(), name="lessons-list"),
    path("lessons/<int:pk>", LessonDetailView.as_view(), name="lessons-detail"),
]
