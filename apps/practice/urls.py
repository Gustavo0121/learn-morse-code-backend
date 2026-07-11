"""Rotas do app practice (montadas sob /api/ no urls raiz)."""

from django.urls import path

from .views import PracticeHistoryView

urlpatterns = [
    path("practice/history", PracticeHistoryView.as_view(), name="practice-history"),
]
