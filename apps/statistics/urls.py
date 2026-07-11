"""Rotas do app statistics (montadas sob /api/ no urls raiz)."""

from django.urls import path

from .views import UserStatisticsView

urlpatterns = [
    path("users/statistics", UserStatisticsView.as_view(), name="users-statistics"),
]
