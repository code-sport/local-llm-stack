import hashlib
import json
import logging
from datetime import datetime

from django.db import transaction, IntegrityError
from django.utils import timezone
from django.utils.text import slugify

from competitions.models import Competition
from competitions.services.organization_service import OrganizationService
from competitions.services.series_service import SeriesService

logger = logging.getLogger(__name__)


class ImportResult:
    """Structured result returned by the import service."""

    def __init__(
        self,
        success: bool,
        competition=None,
        errors=None,
        duplicate: bool = False,
    ):
        self.success = success
        self.competition = competition
        self.errors = errors or []
        self.duplicate = duplicate

    def to_dict(self):
        return {
            "success": self.success,
            "competition_id": self.competition.id if self.competition else None,
            "competition_slug": self.competition.slug if self.competition else None,
            "errors": self.errors,
            "duplicate": self.duplicate,
        }


class CompetitionImportService:
    """
    Validate and import a competition from a parsed info.json dictionary.

    All database operations execute inside a single atomic transaction.
    """

    REQUIRED_FIELDS = ["name", "date", "organization"]

    @staticmethod
    def _compute_import_hash(data: dict) -> str:
        """Deterministic SHA-256 hash of the normalized input data."""
        normalized = json.dumps(
            data, sort_keys=True, ensure_ascii=False, default=str
        )
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @staticmethod
    def _validate(data: dict) -> list:
        """Validate input data structure. Returns list of error messages (empty = valid)."""
        errors = []
        for field in CompetitionImportService.REQUIRED_FIELDS:
            value = data.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                errors.append(f"Missing or empty required field: {field}")

        if "date" in data and data["date"]:
            try:
                datetime.strptime(str(data["date"]), "%Y-%m-%d")
            except ValueError:
                errors.append(
                    f"Invalid date format: {data['date']!r}. Expected YYYY-MM-DD."
                )

        return errors

    @staticmethod
    def import_competition(data: dict, file_path: str = "") -> "ImportResult":
        """
        Main entry point.

        1. Validate input
        2. Check for duplicates (fast path via import_hash)
        3. Resolve related entities and create Competition inside a transaction
        """
        # --- Validate ---
        errors = CompetitionImportService._validate(data)
        if errors:
            return ImportResult(success=False, errors=errors)

        # --- Idempotency check ---
        import_hash = CompetitionImportService._compute_import_hash(data)
        existing = Competition.objects.filter(import_hash=import_hash).first()
        if existing:
            logger.info(
                "Duplicate import detected: hash=%s competition=%s",
                import_hash,
                existing.slug,
            )
            return ImportResult(success=True, competition=existing, duplicate=True)

        # --- Atomic import ---
        try:
            with transaction.atomic():
                organization, _org_created = OrganizationService.resolve(
                    name=data["organization"],
                    website=data.get("organization_website", ""),
                )

                series, _series_created = SeriesService.resolve(
                    name=data.get("series", ""),
                    description=data.get("series_description", ""),
                )

                slug = slugify(data["name"])
                if not slug:
                    return ImportResult(
                        success=False,
                        errors=[
                            f"Cannot derive slug from competition name: {data['name']!r}"
                        ],
                    )

                # Collect extra fields into metadata
                mapped_fields = {
                    "name", "date", "venue", "city", "country",
                    "organization", "organization_website",
                    "series", "series_description",
                }
                metadata = {k: v for k, v in data.items() if k not in mapped_fields}

                competition = Competition.objects.create(
                    name=data["name"].strip(),
                    slug=slug,
                    date=data["date"],
                    venue=data.get("venue", ""),
                    city=data.get("city", ""),
                    country=data.get("country", ""),
                    organization=organization,
                    series=series,
                    status=Competition.Status.IMPORTED,
                    metadata=metadata,
                    imported_at=timezone.now(),
                    imported_from_file=file_path,
                    import_hash=import_hash,
                )

                logger.info(
                    "Imported competition: %s (org=%s, series=%s, slug=%s)",
                    competition.name,
                    organization.slug,
                    series.slug if series else "N/A",
                    competition.slug,
                )

                return ImportResult(success=True, competition=competition)

        except IntegrityError as exc:
            # Catches duplicate import_hash race condition
            logger.warning("IntegrityError during import (likely race): %s", exc)
            existing = Competition.objects.filter(import_hash=import_hash).first()
            if existing:
                return ImportResult(
                    success=True, competition=existing, duplicate=True
                )
            return ImportResult(
                success=False, errors=[f"Database integrity error: {exc}"]
            )

        except Exception as exc:
            logger.exception("Unexpected error during competition import")
            return ImportResult(success=False, errors=[str(exc)])
