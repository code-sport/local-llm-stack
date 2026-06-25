from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model providing auto-managed created_at / updated_at fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Organization(TimeStampedModel):
    """A governing body or federation that organizes competitions."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    website = models.URLField(max_length=500, blank=True, default="")

    class Meta:
        ordering = ["name"]
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

    def __str__(self):
        return self.name


class CompetitionSeries(TimeStampedModel):
    """A named series or tour that competitions belong to (e.g. Grand Slam, World Cup)."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["name"]
        verbose_name = "Competition Series"
        verbose_name_plural = "Competition Series"

    def __str__(self):
        return self.name


class Competition(TimeStampedModel):
    """A single competition event with date, location, and organizational references."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IMPORTED = "imported", "Imported"
        FAILED = "failed", "Failed"

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    date = models.DateField()
    venue = models.CharField(max_length=500, blank=True, default="")
    city = models.CharField(max_length=255, blank=True, default="")
    country = models.CharField(max_length=255, blank=True, default="")

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="competitions",
    )
    series = models.ForeignKey(
        CompetitionSeries,
        on_delete=models.SET_NULL,
        related_name="competitions",
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    metadata = models.JSONField(default=dict, blank=True)

    imported_at = models.DateTimeField(null=True, blank=True)
    imported_from_file = models.CharField(max_length=500, blank=True, default="")

    import_hash = models.CharField(
        max_length=64,
        unique=True,
        help_text="SHA-256 of normalized input JSON for idempotency",
    )

    class Meta:
        ordering = ["-date", "name"]
        verbose_name = "Competition"
        verbose_name_plural = "Competitions"

    def __str__(self):
        return f"{self.name} ({self.date})"
