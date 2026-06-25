"""Integration tests for CompetitionImportService against a real test database."""

import pytest
from django.test import TestCase

from competitions.models import Competition, Organization, CompetitionSeries
from competitions.services.import_service import CompetitionImportService


@pytest.mark.django_db
class TestImportIntegration(TestCase):
    """Full-stack integration tests: real DB, real service, no mocking."""

    def setUp(self):
        self.valid_data = {
            "name": "Paris Grand Slam 2026",
            "date": "2026-03-15",
            "venue": "Accor Arena",
            "city": "Paris",
            "country": "France",
            "organization": "IJF",
            "series": "Grand Slam",
        }

    def test_full_import_creates_all_records(self):
        """Complete valid import creates Competition, Organization, and Series."""
        result = CompetitionImportService.import_competition(self.valid_data)

        assert result.success is True
        assert result.duplicate is False
        assert result.competition.name == "Paris Grand Slam 2026"
        assert result.competition.organization.name == "IJF"
        assert result.competition.series.name == "Grand Slam"
        assert Competition.objects.count() == 1
        assert Organization.objects.count() == 1
        assert CompetitionSeries.objects.count() == 1

    def test_duplicate_import_returns_existing(self):
        """Importing identical data twice returns duplicate=True, no new row."""
        first_result = CompetitionImportService.import_competition(
            self.valid_data
        )
        second_result = CompetitionImportService.import_competition(
            self.valid_data
        )

        assert second_result.duplicate is True
        assert second_result.competition.id == first_result.competition.id
        assert Competition.objects.count() == 1

    def test_import_without_series(self):
        """Omitting the series field results in series=None."""
        data = {k: v for k, v in self.valid_data.items() if k != "series"}
        result = CompetitionImportService.import_competition(data)

        assert result.success is True
        assert result.competition.series is None
        assert CompetitionSeries.objects.count() == 0

    def test_import_with_empty_series(self):
        """An empty series string results in series=None."""
        data = {**self.valid_data, "series": ""}
        result = CompetitionImportService.import_competition(data)

        assert result.success is True
        assert result.competition.series is None

    def test_unknown_organization_is_auto_created(self):
        """Import with a new organization name creates the org record."""
        data = {**self.valid_data, "organization": "New Federation"}
        result = CompetitionImportService.import_competition(data)

        assert result.success is True
        org = Organization.objects.get(slug="new-federation")
        assert org.name == "New Federation"

    def test_known_organization_is_reused(self):
        """Importing two competitions under the same org reuses the org."""
        CompetitionImportService.import_competition(self.valid_data)

        data2 = {
            **self.valid_data,
            "name": "Paris Grand Slam 2027",
            "date": "2027-03-15",
        }
        result = CompetitionImportService.import_competition(data2)

        assert result.success is True
        assert Organization.objects.count() == 1

    def test_extra_fields_stored_in_metadata(self):
        """Unknown fields in the input are preserved in the metadata JSONField."""
        data = {
            **self.valid_data,
            "weight_categories": ["-60kg", "-66kg"],
            "referee": "John Doe",
        }
        result = CompetitionImportService.import_competition(data)

        assert result.competition.metadata["weight_categories"] == [
            "-60kg",
            "-66kg",
        ]
        assert result.competition.metadata["referee"] == "John Doe"

    def test_missing_required_field_fails(self):
        """Missing a required field should return an error without creating records."""
        data = {"name": "Incomplete", "date": "2026-03-15"}  # missing org
        result = CompetitionImportService.import_competition(data)

        assert result.success is False
        assert Competition.objects.count() == 0
        assert Organization.objects.count() == 0

    def test_invalid_date_fails(self):
        """An unparseable date should fail without creating records."""
        data = {
            **self.valid_data,
            "date": "not-a-date",
        }
        result = CompetitionImportService.import_competition(data)

        assert result.success is False
        assert Competition.objects.count() == 0

    def test_import_result_to_dict(self):
        """ImportResult.to_dict() returns a serializable dict."""
        result = CompetitionImportService.import_competition(self.valid_data)
        d = result.to_dict()

        assert d["success"] is True
        assert d["competition_id"] == result.competition.id
        assert d["competition_slug"] == result.competition.slug
        assert d["errors"] == []
        assert d["duplicate"] is False
