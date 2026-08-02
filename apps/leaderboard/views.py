"""Views do app leaderboard."""

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LeaderboardEntrySerializer, LeaderboardQuerySerializer
from .services import get_leaderboard


class LeaderboardView(APIView):
    """GET /api/leaderboard — ranking por velocidade, modo e período."""

    def get(self, request: Request) -> Response:
        query = LeaderboardQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        entries = get_leaderboard(**query.validated_data)
        return Response(LeaderboardEntrySerializer(entries, many=True).data)
