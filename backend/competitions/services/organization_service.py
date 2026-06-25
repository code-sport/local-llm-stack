from django.utils.text import slugify
from competitions.models import Organization


class OrganizationService:
    """Resolves an organization name to an Organization record (find or create)."""

    @staticmethod
    def resolve(name: str, website: str = "") -> tuple:
        """
        Find an existing Organization by slug, or create one.

        Returns (Organization, created: bool).
        Raises ValueError if the name cannot produce a valid slug.
        """
        slug = slugify(name)
        if not slug:
            raise ValueError(
                f"Cannot derive slug from organization name: {name!r}"
            )

        org, created = Organization.objects.get_or_create(
            slug=slug,
            defaults={"name": name.strip(), "website": website},
        )

        if not created:
            changed = False
            if org.name != name.strip():
                org.name = name.strip()
                changed = True
            if website and org.website != website:
                org.website = website
                changed = True
            if changed:
                org.save()

        return org, created
