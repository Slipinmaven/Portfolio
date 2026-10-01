# Copilot instructions

## Core architecture

Follow this project rule at all times:

Endpoint -> Service -> Repository -> Database

Do not create direct endpoint-to-repository access. Do not move DB calls into endpoints. Do not use repository logic inside HTTP adapters. Keep business rules in services.

## Required workflow

Before changing a domain:

1. inspect the endpoint
2. inspect the service
3. inspect the repository
4. inspect the model and schema
5. inspect the dependency and migration setup
6. inspect the relevant tests

## Forbidden patterns

- Endpoint imports repositories directly
- Endpoint calls session.execute(), session.scalar(), session.scalars(), session.add(), session.delete()
- Endpoint contains publication, slug, or project validation logic
- Service raises HTTPException or imports FastAPI response objects
- Repository raises HTTPException or checks admin authorization
- Models are used as request/response schemas
- Base.metadata.create_all() is used for schema creation

## Allowed patterns

- endpoint validates HTTP inputs and translates domain exceptions to HTTP status codes
- service owns business logic and orchestration
- repository owns SQLAlchemy query and persistence behavior
- dependency injects session and auth context
- Alembic handles schema migration

## Project-specific conventions

- status and publication_status are separate concepts
- public endpoints expose only published items
- admin endpoints require the existing admin dependency
- slugs must remain stable unless explicitly updated
- project cover is controlled by project_media.is_cover; only one cover per project is valid
- media is reusable; project_media stores project-specific metadata
- use the existing app/db/session.py and app/dependencies/database.py patterns

## Verification

After code changes, run the relevant backend test suite and keep the architecture aligned with the project’s existing patterns.
