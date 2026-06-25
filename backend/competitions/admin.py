from django.contrib import admin
from .models import Organization, CompetitionSeries, Competition


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "website", "created_at"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}
    readonly_fields = ["created_at", "updated_at"]


@admin.register(CompetitionSeries)
class CompetitionSeriesAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = [
        "name", "date", "organization", "series",
        "status", "imported_at",
    ]
    list_filter = ["status", "organization", "series", "country"]
    search_fields = ["name", "slug", "venue", "city"]
    prepopulated_fields = {"slug": ["name"]}
    readonly_fields = [
        "import_hash", "imported_at", "imported_from_file",
        "created_at", "updated_at",
    ]
    date_hierarchy = "date"
