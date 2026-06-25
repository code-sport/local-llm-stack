"""Unit tests for CompetitionImportService with mocked database layer."""

from unittest.mock import patch, MagicMock

from competitions.services.import_service import (
    CompetitionImportService,
    ImportResult,
)


class TestValidation:
    """Tests for the _validate static method."""

    def test_requires_all_fields(self):
        """Missing required fields should return errors."""
        data = {"name": "Test", "date": "2026-06-15"}
        errors = CompetitionImportService._validate(data)
        assert len(errors) == 1
        assert "organization" in errors[0]

    def test_empty_required_field_fails(self):
        """Empty string for a required field should fail."""
        data = {"name": "", "date": "2026-06-15", "organization": "IJF"}
        errors = CompetitionImportService._validate(data)
        assert len(errors) == 1
        assert "name" in errors[0]

    def test_invalid_date_format(self):
        """Non-parseable date should fail."""
        data = {
            "name": "Test", "date": "not-a-date", "organization": "IJF",
        }
        errors = CompetitionImportService._validate(data)
        assert any("date" in e.lower() for e in errors)

    def test_valid_data_passes(self):
        """Valid input should produce no errors."""
        data = {
            "name": "Paris Grand Slam",
            "date": "2026-03-15",
            "organization": "IJF",
        }
        errors = CompetitionImportService._validate(data)
        assert errors == []


class TestImportHash:
    """Tests for the _compute_import_hash static method."""

    def test_deterministic_regardless_of_key_order(self):
        """Same data with different key order should produce identical hash."""
        data1 = {"name": "A", "date": "2026-01-01", "organization": "X"}
        data2 = {"organization": "X", "date": "2026-01-01", "name": "A"}
        assert CompetitionImportService._compute_import_hash(
            data1
        ) == CompetitionImportService._compute_import_hash(data2)

    def test_different_data_different_hash(self):
        """Different data should produce different hashes."""
        data1 = {"name": "A", "date": "2026-01-01", "organization": "X"}
        data2 = {"name": "B", "date": "2026-01-01", "organization": "X"}
        assert CompetitionImportService._compute_import_hash(
            data1
        ) != CompetitionImportService._compute_import_hash(data2)

    def test_hash_is_sha256_hexdigest(self):
        """The hash should be a 64-character hex string (SHA-256)."""
        data = {"name": "A", "date": "2026-01-01", "organization": "X"}
        h = CompetitionImportService._compute_import_hash(data)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


class TestImportServiceWithMocks:
    """Tests for import_competition with mocked persistence layer."""

    @patch("competitions.services.import_service.Competition.objects.create")
    @patch("competitions.services.import_service.SeriesService.resolve")
    @patch("competitions.services.import_service.OrganizationService.resolve")
    @patch("competitions.services.import_service.transaction.atomic")
    @patch("competitions.services.import_service.Competition.objects.filter")
    @patch("competitions.services.import_service.CompetitionImportService._validate")
    def test_happy_path(
        self,
        mock_validate,
        mock_filter,
        mock_atomic,
        mock_org_resolve,
        mock_series_resolve,
        mock_create,
    ):
        """Valid input should succeed, calling org/series resolution correctly."""
        mock_validate.return_value = []
        mock_filter.return_value.first.return_value = None
        mock_atomic.return_value.__enter__.return_value = None

        mock_org = MagicMock(spec=["slug", "name"])
        mock_org.slug = "ijf"
        mock_org_resolve.return_value = (mock_org, False)

        mock_series = MagicMock(spec=["slug", "name"])
        mock_series.slug = "grand-slam"
        mock_series_resolve.return_value = (mock_series, False)

        mock_competition = MagicMock(spec=["slug", "id", "name"])
        mock_competition.slug = "paris-grand-slam"
        mock_competition.id = 1
        mock_create.return_value = mock_competition

        data = {
            "name": "Paris Grand Slam",
            "date": "2026-03-15",
            "organization": "IJF",
            "series": "Grand Slam",
        }

        result = CompetitionImportService.import_competition(data)

        assert result.success is True
        assert result.duplicate is False
        mock_org_resolve.assert_called_once_with(
            name="IJF", website=""
        )
        mock_series_resolve.assert_called_once_with(
            name="Grand Slam", description=""
        )

    @patch("competitions.services.import_service.CompetitionImportService._validate")
    def test_validation_failure_returns_errors(self, mock_validate):
        """Validation errors should abort the import before any DB access."""
        mock_validate.return_value = ["Missing required field: organization"]

        result = CompetitionImportService.import_competition(
            {"name": "Test", "date": "2026-01-01"}
        )

        assert result.success is False
        assert len(result.errors) == 1
        assert "organization" in result.errors[0]

    @patch("competitions.services.import_service.Competition.objects.filter")
    @patch("competitions.services.import_service.CompetitionImportService._validate")
    def test_duplicate_import_returns_existing(
        self, mock_validate, mock_filter
    ):
        """When import_hash matches an existing record, return duplicate=True."""
        mock_validate.return_value = []
        mock_competition = MagicMock(slug="paris-grand-slam")
        mock_filter.return_value.first.return_value = mock_competition

        data = {
            "name": "Paris Grand Slam",
            "date": "2026-03-15",
            "organization": "IJF",
        }

        result = CompetitionImportService.import_competition(data)

        assert result.success is True
        assert result.duplicate is True
        assert result.competition is mock_competition

    @patch("competitions.services.import_service.CompetitionImportService._validate")
    def test_empty_data_fails_validation(self, mock_validate):
        """Completely empty data should fail validation."""
        mock_validate.return_value = [
            "Missing or empty required field: name",
            "Missing or empty required field: date",
            "Missing or empty required field: organization",
        ]

        result = CompetitionImportService.import_competition({})

        assert result.success is False
        assert len(result.errors) == 3
