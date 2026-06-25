import json
import logging
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from competitions.services.import_service import CompetitionImportService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import a competition from an info.json file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            "-f",
            type=str,
            required=True,
            help="Path to the info.json file",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file"]).resolve()

        if not file_path.exists():
            raise CommandError(f"File not found: {file_path}")

        if file_path.suffix.lower() != ".json":
            self.stdout.write(
                self.style.WARNING(
                    f"File does not have .json extension: {file_path}"
                )
            )

        try:
            with open(file_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON in {file_path}: {exc}")
        except IOError as exc:
            raise CommandError(f"Error reading {file_path}: {exc}")

        result = CompetitionImportService.import_competition(
            data=data,
            file_path=str(file_path),
        )

        if not result.success:
            self.stderr.write(self.style.ERROR("Import failed:"))
            for error in result.errors:
                self.stderr.write(self.style.ERROR(f"  - {error}"))
            raise CommandError("Import failed")

        if result.duplicate:
            self.stdout.write(
                self.style.WARNING(
                    f"Duplicate import. Existing competition: "
                    f"{result.competition.name} (slug={result.competition.slug})"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully imported competition: "
                    f"{result.competition.name} "
                    f"(slug={result.competition.slug}, id={result.competition.id})"
                )
            )
