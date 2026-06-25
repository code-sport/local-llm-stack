import hashlib

import factory
from django.utils.text import slugify

from competitions.models import Organization, CompetitionSeries, Competition


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Sequence(lambda n: f"Organization {n}")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    website = ""


class CompetitionSeriesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CompetitionSeries

    name = factory.Sequence(lambda n: f"Series {n}")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    description = ""


class CompetitionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Competition

    name = factory.Sequence(lambda n: f"Competition {n}")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    date = "2026-06-15"
    venue = "Test Venue"
    city = "Test City"
    country = "Test Country"
    organization = factory.SubFactory(OrganizationFactory)
    series = None
    status = Competition.Status.IMPORTED
    metadata = {}
    imported_from_file = ""
    import_hash = factory.Sequence(
        lambda n: hashlib.sha256(f"test{n}".encode()).hexdigest()
    )
