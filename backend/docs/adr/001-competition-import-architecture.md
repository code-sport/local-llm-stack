# ADR 001: Competition Import Application Architecture

**Status:** Accepted  
**Date:** 2026-06-26  
**Author:** code.sport

## Context

The `claude-local-stack` repository provides a Docker-based local AI stack. We need to add a Competition Import Application Layer that ingests `info.json` payloads, creates `Competition` records with `Organization` and `CompetitionSeries` references, and exposes this functionality via both a REST API and a CLI management command.

This is the first application code in the repository. The decisions below establish the architectural foundation for future expansion (CRUD endpoints, user authentication, bulk import, etc.).

---

## Decision 1: Django + Django REST Framework

**Choice:** Django 5.x with Django REST Framework over Flask, FastAPI, or plain Python.

**Rationale:**
- The domain (competition management with structured models, foreign-key relationships, audit trails) maps naturally to Django's ORM.
- Django provides built-in migrations, admin interface, authentication, and permission system — all likely needed as the API grows.
- DRF provides serialization, request parsing, browsable API, and view sets without additional libraries.
- The "batteries-included" philosophy reduces the number of third-party decisions early on.

**Trade-off:** Django has more startup boilerplate than FastAPI. For the current scope (a single import endpoint), FastAPI would be lighter. However, the expected growth trajectory (multiple CRUD endpoints, admin UI, auth) favors Django.

---

## Decision 2: Django ORM (not SQLAlchemy)

**Choice:** Django ORM over SQLAlchemy.

**Rationale:**
- Tighter integration with Django's migration framework, admin, and DRF serializers.
- Sufficient for the domain complexity (3 models with simple FK relationships).
- SQLAlchemy would be preferable only if we needed complex window queries, multi-database sharding, or async access — none of which are requirements for V1.

---

## Decision 3: Service Layer Pattern

**Choice:** Business logic lives in standalone service classes (`*Service`), not in views or management commands.

**Rationale:**
- **Reusability:** The import logic is callable from both the REST API (`views.py`) and the CLI (`management/command`).
- **Testability:** Services can be unit-tested without HTTP or CLI harness.
- **Transaction boundary:** The `transaction.atomic()` scope is explicit in the service method, not split across view layers.

**Structure:**
- `OrganizationService.resolve()` — find-or-create organizations
- `SeriesService.resolve()` — find-or-create competition series  
- `CompetitionImportService.import_competition()` — orchestrates the full import flow

---

## Decision 4: Content-Hash Idempotency

**Choice:** SHA-256 of normalized input JSON stored as a unique column (`import_hash`) on the `Competition` model.

**Rationale:**
- Simpler than a separate import-log table or application-level deduplication.
- The `unique=True` constraint provides a database-enforced guarantee.
- Fast-path check (query by hash) before entering the transaction.
- Race-condition recovery via `IntegrityError` catch-and-re-query.

**Trade-off:** Requires computing the hash for every import request. For the expected payload size (a few KB), this is negligible.

---

## Decision 5: Find-or-Create by Slug for Related Entities

**Choice:** Organizations and CompetitionSeries are resolved by slug (derived from name via Django's `slugify()`).

**Rationale:**
- "IJF" always produces slug `ijf`, so two imports referencing "IJF" resolve to the same Organization.
- No alias table needed initially.
- The service updates name/website fields if the existing record differs (eventual consistency).

**Limitation:** Name variations ("IJF" vs "International Judo Federation") produce different slugs. A future `OrganizationAlias` model can resolve this.

---

## Decision 6: Nullable CompetitionSeries

**Choice:** `Competition.series` is nullable (`null=True, blank=True`) with `on_delete=SET_NULL`.

**Rationale:**
- Not all competitions belong to a named series (e.g., local club tournaments).
- `SET_NULL` prevents cascade-deletion of competitions if a series is removed.
- The import service treats a missing or empty `series` field as "no series."

---

## Decision 7: SQLite for Development, PostgreSQL for Production

**Choice:** Default database engine is SQLite (zero-config). `DATABASE_URL` env var switches to PostgreSQL.

**Rationale:**
- SQLite requires no Docker database service, no user creation, no connection setup — a developer can `pip install` and `migrate` immediately.
- PostgreSQL is the production target (used in the Docker Compose stack).
- Django's ORM abstracts the differences; no code changes are needed between environments.

---

## Decision 8: Atomic Transaction for Import

**Choice:** All write operations (Organization find-or-create, Series find-or-create, Competition create) execute inside `django.db.transaction.atomic()`.

**Rationale:**
- Guarantees all-or-nothing semantics. If Competition creation fails after Organization creation, the Organization is rolled back.
- Prevents orphan records.
- Input validation happens *outside* the transaction to avoid holding database locks during validation.

---

## Decision 9: Metadata JSONField

**Choice:** Any unrecognized fields in the import payload are stored as-is in a `metadata` JSONField on `Competition`.

**Rationale:**
- Makes the system forward-compatible with future `info.json` schema extensions.
- A competition entry might include sport-specific fields (weight categories, match format, referee assignments) that don't warrant dedicated columns.
- JSONField supports querying (though not indexed by default in all databases).

---

## Consequences

- All future competition-related endpoints should follow the service-layer pattern.
- Adding new required fields to `info.json` requires: (a) updating the model, (b) creating a migration, (c) updating the input serializer, (d) updating the import service if non-trivial mapping is needed.
- The metadata JSONField allows adding optional fields without migrations — but also means no database-level validation on those fields.
