from rest_framework import serializers
from competitions.models import Competition, Organization, CompetitionSeries


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id", "name", "slug", "website",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]


class CompetitionSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionSeries
        fields = [
            "id", "name", "slug", "description",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]


class CompetitionSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    series = CompetitionSeriesSerializer(read_only=True)

    class Meta:
        model = Competition
        fields = [
            "id", "name", "slug", "date", "venue", "city", "country",
            "organization", "series", "status", "metadata",
            "imported_at", "imported_from_file",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "slug", "status", "imported_at",
            "imported_from_file", "created_at", "updated_at",
        ]


class CompetitionImportInputSerializer(serializers.Serializer):
    """Validates the incoming info.json payload for a competition import."""

    name = serializers.CharField(required=True)
    date = serializers.DateField(required=True)
    organization = serializers.CharField(required=True)
    organization_website = serializers.URLField(
        required=False, allow_blank=True, default=""
    )
    series = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    series_description = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    venue = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    city = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    country = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
