# Backend architecture

## Required request flow

All HTTP traffic follows the same boundary structure:

HTTP
↓
Middleware
↓
Dependency injection / request-scoped infrastructure
↓
Endpoint / router
↓
Service
↓
Repository
↓
SQLAlchemy / database

This project allows cross-cutting HTTP concerns in middleware, but direct endpoint-to-repository access is forbidden.

## Layer responsibilities

### Middleware

Middleware is for cross-cutting HTTP concerns only.

Allowed:

- request correlation / request IDs
- response logging
- CORS configuration
- timing and tracing
- request context storage
- security headers where applicable

Forbidden:

- project business logic
- project validation
- repository access
- database queries
- publication logic
- slug logic

### Dependencies

Dependencies provide request-scoped infrastructure and authorization.

Allowed:

- database sessions
- current authenticated user
- admin guard
- common request injection

Forbidden:

- hidden business logic
- project publication checks
- domain validation that belongs in services
- direct SQLAlchemy persistence logic

### Endpoints / routers

Endpoints adapt HTTP requests to domain operations.

Allowed:

- path and query parameters
- request schema validation
- calling a service via dependency injection
- returning response schemas
- translating domain exceptions to HTTP status codes

Forbidden:

- importing repositories directly
- instantiating repositories
- calling session.execute(), session.scalar(), session.scalars(), session.add(), or session.delete()
- implementing slug generation or publication rules
- implementing persistence logic
- writing business validation that belongs in services

### Services

Services own application and domain orchestration.

Allowed:

- business validation
- publication transitions
- slug conflict checks
- relationship synchronization
- transaction orchestration
- calling repositories as needed

Forbidden:

- direct HTTP response handling
- FastAPI Request/Response dependencies
- HTTPException raising for domain rules
- raw SQLAlchemy session access

### Repositories

Repositories handle persistence and query behavior only.

Allowed:

- select() / scalar() / scalars()
- add(), update(), delete() patterns
- query relationship data
- query by id, slug, or status

Forbidden:

- HTTPException
- Request or Response types
- authorization checks
- admin policy
- API response formatting
- domain publication rules

### Models

Models define the database schema and ORM structure.

Allowed:

- table mapping
- relationship metadata
- constraints and indexes
- timestamps

Forbidden:

- HTTP behavior
- API response formatting
- business validation that belongs to the service layer

### Schemas

Schemas define API contracts.

Allowed:

- request validation objects
- public/admin response objects
- typed serialization contracts

Forbidden:

- direct database/session access
- business logic
- router logic

## Project domain rules

### Status separation

Development status and publication status are independent.

Development status:

- planning
- in_progress
- completed
- archived

Publication status:

- draft
- published

### Publication logic

Publishing must be explicit.

When project becomes published:

- publication_status = published
- published_at = current UTC timestamp

When project becomes draft:

- publication_status = draft
- published_at = null

The public endpoint exposes only projects that are published and not archived.

### Slug behavior

- slugs must be URL-safe
- slugs must be unique
- slug generation must be stable after creation unless an explicit update is requested
- the database remains the final source of uniqueness

### Technology rules

- technologies are first-class entities
- technology association uses a link table with unique (project_id, technology_id)
- ordering is relationship-specific, not global technology state

### Project media rules

- media is a reusable asset model
- project media is relationship metadata tied to a project
- project cover is controlled by the project_media.is_cover flag
- there can be at most one active cover per project

### Admin vs public

- admin responses may include management metadata
- public endpoints must not expose draft or admin-only data
- authorization must be enforced with current dependency guards

## Forbidden patterns

These patterns are not allowed in this repository:

- Endpoint -> Repository direct access
- Endpoint -> session.execute()
- Endpoint -> database write calls
- Service -> HTTPException-based transport layer
- Repository -> FastAPI Request/Response
- Repository -> authorization policy
- Model -> service logic
- Router -> persistence implementation

## Required architectural enforcement

Before modifying a domain, inspect:

- endpoint
- service
- repository
- model
- schema
- dependency
- migration
- test

Do not create new infrastructure that conflicts with the established patterns.

Use the current session factory and dependency injection architecture.

Use Alembic for schema changes.

Do not call Base.metadata.create_all() in application startup.

## Testing requirements

Changes must be validated with the existing backend test suite and with strongly targeted tests for project-domain rules.

## Useful file map

Relevant modules:

- app/api/v1/endpoints/projects.py
- app/api/v1/endpoints/technologies.py
- app/api/v1/endpoints/auth.py
- app/api/v1/endpoints/health.py
- app/services/project.py
- app/services/auth.py
- app/repositories/project.py
- app/repositories/technology.py
- app/models/project.py
- app/models/technology.py
- app/models/media.py
- app/schemas/project.py
- app/dependencies/services.py
- app/db/session.py
