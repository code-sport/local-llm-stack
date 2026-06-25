from django.utils.text import slugify
from competitions.models import CompetitionSeries


class SeriesService:
    """Resolves a series name to a CompetitionSeries record (find or create)."""

    @staticmethod
    def resolve(name: str, description: str = "") -> tuple:
        """
        Find an existing CompetitionSeries by slug, or create one.

        Returns (CompetitionSeries | None, created: bool).
        Returns (None, False) when name is empty or whitespace-only.
        """
        if not name or not name.strip():
            return None, False

        slug = slugify(name)
        if not slug:
            return None, False

        series, created = CompetitionSeries.objects.get_or_create(
            slug=slug,
            defaults={"name": name.strip(), "description": description},
        )

        if not created:
            changed = False
            if series.name != name.strip():
                series.name = name.strip()
                changed = True
            if description and series.description != description:
                series.description = description
                changed = True
            if changed:
                series.save()

        return series, created
