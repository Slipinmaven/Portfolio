from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ProjectValidationError
from app.models.media import Media
from app.models.project import Project, ProjectMedia
from app.repositories.media import MediaRepository
from app.repositories.project import ProjectRepository
from app.repositories.technology import TechnologyRepository
from app.schemas.project import ProjectCreate, ProjectPublicResponse
from app.services.project import ProjectService


def project_service(app_session) -> ProjectService:
    return ProjectService(ProjectRepository(app_session), TechnologyRepository(app_session), MediaRepository(app_session))


@pytest.mark.asyncio
async def test_project_response_exposes_loaded_associations(app_session):
    project = Project(title="API", slug="api")
    app_session.add(project)
    await app_session.flush()

    stored = await ProjectRepository(app_session).get_by_id(project.id)
    response = ProjectPublicResponse.model_validate(stored)

    assert response.technologies == []
    assert response.media == []


@pytest.mark.asyncio
async def test_project_service_rejects_invalid_dates_and_slugs(app_session):
    now = datetime.now(timezone.utc)
    service = project_service(app_session)

    with pytest.raises(ProjectValidationError, match="completion"):
        await service.create_project(ProjectCreate(title="Invalid dates", started_at=now, completed_at=now - timedelta(days=1)))

    with pytest.raises(ProjectValidationError, match="slug"):
        await service.create_project(ProjectCreate(title="Invalid slug", slug="!!!"))


@pytest.mark.asyncio
async def test_publish_and_unpublish_update_published_at(app_session):
    project = Project(title="Publishable", slug="publishable")
    app_session.add(project)
    await app_session.flush()
    service = project_service(app_session)

    await service.publish(project)
    assert project.publication_status == "published"
    assert project.published_at is not None

    await service.unpublish(project)
    assert project.publication_status == "draft"
    assert project.published_at is None


@pytest.mark.asyncio
async def test_project_has_at_most_one_cover_media(app_session):
    project = Project(title="Media project", slug="media-project")
    first = Media(storage_key="first.png", mime_type="image/png")
    second = Media(storage_key="second.png", mime_type="image/png")
    app_session.add_all([project, first, second])
    await app_session.flush()
    app_session.add_all([
        ProjectMedia(project_id=project.id, media_id=first.id, is_cover=True),
        ProjectMedia(project_id=project.id, media_id=second.id, is_cover=True),
    ])

    with pytest.raises(IntegrityError):
        await app_session.flush()