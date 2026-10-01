import re
import uuid
from datetime import datetime, timezone

from app.core.exceptions import ProjectConflictError, ProjectValidationError, TechnologyConflictError, TechnologyNotFoundError
from app.models.media import Media
from app.models.project import Project, ProjectFeature, ProjectMedia, ProjectTechnology
from app.models.technology import Technology
from app.repositories.media import MediaRepository
from app.repositories.project import ProjectRepository
from app.repositories.technology import TechnologyRepository


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower().strip())
    return slug.strip("-")


class ProjectService:
    def __init__(self, project_repo: ProjectRepository, technology_repo: TechnologyRepository, media_repo: MediaRepository):
        self.project_repo = project_repo
        self.technology_repo = technology_repo
        self.media_repo = media_repo

    async def list_public_projects(self):
        return list(await self.project_repo.list_public())

    async def list_admin_projects(self):
        return list(await self.project_repo.list_admin())

    async def get_project_by_id(self, project_id: uuid.UUID) -> Project | None:
        return await self.project_repo.get_by_id(project_id)

    async def get_project_by_slug(self, slug: str) -> Project | None:
        project = await self.project_repo.get_by_slug(slug)
        if not project or project.publication_status != "published" or project.status == "archived":
            return None
        return project

    async def create_project(self, payload) -> Project:
        title = (payload.title or "").strip()
        if not title:
            raise ProjectValidationError("Project title is required")

        slug = (payload.slug or slugify(title)).strip()
        slug = slugify(slug)
        if not slug:
            raise ProjectValidationError("Project slug is invalid")
        if payload.started_at and payload.completed_at and payload.completed_at < payload.started_at:
            raise ProjectValidationError("Project completion cannot precede its start")

        existing = await self.project_repo.get_by_slug(slug)
        if existing:
            raise ProjectConflictError("Project slug already exists")

        project = Project(
            title=title,
            slug=slug,
            short_description=payload.short_description,
            description=payload.description,
            problem=payload.problem,
            solution=payload.solution,
            technical_details=payload.technical_details,
            technical_decisions=payload.technical_decisions,
            challenges=payload.challenges,
            outcome=payload.outcome,
            started_at=payload.started_at,
            completed_at=payload.completed_at,
            status=payload.status or "planning",
            publication_status=payload.publication_status or "draft",
            is_featured=payload.is_featured,
            display_order=payload.display_order,
            github_url=str(payload.github_url) if payload.github_url else None,
            live_url=str(payload.live_url) if payload.live_url else None,
            meta_title=payload.meta_title,
            meta_description=payload.meta_description,
        )
        if project.publication_status == "published":
            project.published_at = datetime.now(timezone.utc)
        await self.project_repo.add(project)

        for tech_id in getattr(payload, "technology_ids", []) or []:
            technology = await self.technology_repo.get_by_id(tech_id)
            if technology is None:
                raise TechnologyNotFoundError(f"Technology {tech_id} not found")
            association = ProjectTechnology(project_id=project.id, technology_id=technology.id, display_order=0)
            await self.project_repo.add_technology(association)

        for index, feature in enumerate(getattr(payload, "feature_titles", []) or []):
            feature_title = (feature or "").strip()
            if not feature_title:
                continue
            await self.project_repo.add_feature(ProjectFeature(project_id=project.id, title=feature_title, display_order=index))

        await self.project_repo.session.commit()
        return await self.project_repo.get_by_id(project.id)

    async def update_project(self, project: Project, payload) -> Project:
        if payload.title is not None:
            title = payload.title.strip()
            if not title:
                raise ProjectValidationError("Project title is required")
            project.title = title
        if payload.slug is not None:
            slug = slugify(payload.slug)
            if not slug:
                raise ProjectValidationError("Project slug is invalid")
            if slug != project.slug:
                existing = await self.project_repo.get_by_slug(slug)
                if existing and existing.id != project.id:
                    raise ProjectConflictError("Project slug already exists")
                project.slug = slug
        if payload.short_description is not None:
            project.short_description = payload.short_description
        if payload.description is not None:
            project.description = payload.description
        if payload.problem is not None:
            project.problem = payload.problem
        if payload.solution is not None:
            project.solution = payload.solution
        if payload.technical_details is not None:
            project.technical_details = payload.technical_details
        if payload.technical_decisions is not None:
            project.technical_decisions = payload.technical_decisions
        if payload.challenges is not None:
            project.challenges = payload.challenges
        if payload.outcome is not None:
            project.outcome = payload.outcome
        if payload.started_at is not None:
            project.started_at = payload.started_at
        if payload.completed_at is not None:
            project.completed_at = payload.completed_at
        if project.started_at and project.completed_at and project.completed_at < project.started_at:
            raise ProjectValidationError("Project completion cannot precede its start")
        if payload.status is not None:
            project.status = payload.status
        if payload.publication_status is not None:
            project.publication_status = payload.publication_status
            if payload.publication_status == "published" and project.published_at is None:
                project.published_at = datetime.now(timezone.utc)
            elif payload.publication_status == "draft":
                project.published_at = None
        if payload.is_featured is not None:
            project.is_featured = payload.is_featured
        if payload.display_order is not None:
            project.display_order = payload.display_order
        if payload.github_url is not None:
            project.github_url = str(payload.github_url)
        if payload.live_url is not None:
            project.live_url = str(payload.live_url)
        if payload.meta_title is not None:
            project.meta_title = payload.meta_title
        if payload.meta_description is not None:
            project.meta_description = payload.meta_description

        await self.project_repo.update(project)
        await self.project_repo.session.commit()
        return project

    async def publish(self, project: Project) -> Project:
        project.publication_status = "published"
        if project.published_at is None:
            project.published_at = datetime.now(timezone.utc)
        await self.project_repo.update(project)
        await self.project_repo.session.commit()
        return project

    async def unpublish(self, project: Project) -> Project:
        project.publication_status = "draft"
        project.published_at = None
        await self.project_repo.update(project)
        await self.project_repo.session.commit()
        return project

    async def attach_technology(self, project: Project, technology_id: uuid.UUID) -> ProjectTechnology:
        if technology_id in {pt.technology_id for pt in project.project_technologies}:
            raise ProjectConflictError("Technology already attached to project")
        technology = await self.technology_repo.get_by_id(technology_id)
        if technology is None:
            raise TechnologyNotFoundError("Technology not found")
        association = ProjectTechnology(project_id=project.id, technology_id=technology.id, display_order=len(project.project_technologies))
        project.project_technologies.append(association)
        await self.project_repo.update(project)
        return association

    async def attach_media(self, project: Project, media_id: uuid.UUID, media_type: str, title: str | None = None, alt_text: str | None = None, caption: str | None = None, display_order: int = 0, is_cover: bool = False) -> ProjectMedia:
        media = await self.media_repo.get_by_id(media_id)
        if media is None:
            raise ProjectValidationError("Media not found")
        association = ProjectMedia(project_id=project.id, media_id=media.id, type=media_type, title=title, caption=caption, alt_text=alt_text, display_order=display_order, is_cover=is_cover)
        if is_cover:
            for existing in project.project_media:
                if existing.is_cover and existing.id != association.id:
                    existing.is_cover = False
        await self.project_repo.add_media(association)
        return association


class TechnologyService:
    def __init__(self, repo: TechnologyRepository):
        self.repo = repo

    async def list_technologies(self):
        return list(await self.repo.list_all())

    async def get_by_id(self, technology_id: uuid.UUID) -> Technology | None:
        return await self.repo.get_by_id(technology_id)

    async def get_by_slug(self, slug: str) -> Technology | None:
        return await self.repo.get_by_slug(slug)

    async def create_technology(self, payload) -> Technology:
        name = (payload.name or "").strip()
        if not name:
            raise ProjectValidationError("Technology name is required")
        slug = slugify(payload.slug or name)
        existing = await self.repo.get_by_slug(slug)
        if existing:
            raise TechnologyConflictError("Technology slug already exists")
        technology = Technology(
            name=name,
            slug=slug,
            short_description=payload.short_description,
            category=payload.category or "other",
            icon=payload.icon,
            display_order=payload.display_order,
            is_featured=payload.is_featured,
        )
        technology = await self.repo.add(technology)
        await self.repo.session.commit()
        return technology

    async def update_technology(self, technology: Technology, payload) -> Technology:
        if payload.name is not None:
            technology.name = payload.name.strip()
        if payload.slug is not None:
            slug = slugify(payload.slug)
            existing = await self.repo.get_by_slug(slug)
            if existing and existing.id != technology.id:
                raise TechnologyConflictError("Technology slug already exists")
            technology.slug = slug
        if payload.short_description is not None:
            technology.short_description = payload.short_description
        if payload.category is not None:
            technology.category = payload.category
        if payload.icon is not None:
            technology.icon = payload.icon
        if payload.display_order is not None:
            technology.display_order = payload.display_order
        if payload.is_featured is not None:
            technology.is_featured = payload.is_featured
        technology = await self.repo.update(technology)
        await self.repo.session.commit()
        return technology
