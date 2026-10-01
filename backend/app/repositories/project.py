from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project, ProjectFeature, ProjectMedia, ProjectTechnology


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _base_query(self) -> Select[tuple[Project]]:
        return select(Project).options(
            selectinload(Project.features),
            selectinload(Project.project_technologies).selectinload(ProjectTechnology.technology),
            selectinload(Project.project_media).selectinload(ProjectMedia.media),
        )

    async def get_by_id(self, project_id: UUID) -> Project | None:
        return await self.session.scalar(self._base_query().where(Project.id == project_id))

    async def get_by_slug(self, slug: str) -> Project | None:
        return await self.session.scalar(self._base_query().where(Project.slug == slug))

    async def list_public(self):
        return await self.session.scalars(
            self._base_query()
            .where(Project.publication_status == "published")
            .where(Project.status != "archived")
            .order_by(Project.display_order.asc(), Project.created_at.desc())
        )

    async def list_admin(self):
        return await self.session.scalars(self._base_query().order_by(Project.display_order.asc(), Project.created_at.desc()))

    async def add(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.flush()
        return project

    async def update(self, project: Project) -> Project:
        await self.session.flush()
        return project

    async def delete(self, project: Project) -> None:
        await self.session.delete(project)
        await self.session.flush()

    async def add_feature(self, feature: ProjectFeature) -> ProjectFeature:
        self.session.add(feature)
        await self.session.flush()
        return feature

    async def add_technology(self, association: ProjectTechnology) -> ProjectTechnology:
        self.session.add(association)
        await self.session.flush()
        return association

    async def add_media(self, association: ProjectMedia) -> ProjectMedia:
        self.session.add(association)
        await self.session.flush()
        return association
