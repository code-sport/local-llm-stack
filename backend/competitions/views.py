from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from competitions.models import Competition
from competitions.serializers import (
    CompetitionImportInputSerializer,
    CompetitionSerializer,
)
from competitions.services.import_service import CompetitionImportService


@api_view(["GET"])
def list_competitions(request):
    """GET /api/competitions/ — list all imported competitions."""
    competitions = Competition.objects.select_related(
        "organization", "series"
    ).all()
    serializer = CompetitionSerializer(competitions, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def import_competition(request):
    """
    POST /api/competitions/import/

    Accepts info.json data in the request body.
    Returns 201 (new), 200 (duplicate), or 422 (validation error).
    """
    input_serializer = CompetitionImportInputSerializer(data=request.data)
    if not input_serializer.is_valid():
        return Response(
            {"success": False, "errors": input_serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    result = CompetitionImportService.import_competition(
        data=input_serializer.validated_data,
        file_path="api",
    )

    if not result.success:
        return Response(
            {"success": False, "errors": result.errors},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    competition_data = CompetitionSerializer(result.competition).data

    if result.duplicate:
        return Response(
            {"success": True, "duplicate": True, "competition": competition_data},
            status=status.HTTP_200_OK,
        )

    return Response(
        {"success": True, "duplicate": False, "competition": competition_data},
        status=status.HTTP_201_CREATED,
    )
