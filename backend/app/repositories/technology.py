from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import ProjectTechnology
from app.models.technology import Technology


class TechnologyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _base_query(self) -> Select[tuple[Technology]]:
        return select(Technology).options(selectinload(Technology.project_technologies).selectinload(ProjectTechnology.project))

    async def get_by_id(self, technology_id: UUID) -> Technology | None:
        return await self.session.scalar(self._base_query().where(Technology.id == technology_id))

    async def get_by_slug(self, slug: str) -> Technology | None:
        return await self.session.scalar(self._base_query().where(Technology.slug == slug))

    async def get_by_name(self, name: str) -> Technology | None:
        return await self.session.scalar(select(Technology).where(Technology.name == name))

    async def list_all(self):
        return await self.session.scalars(self._base_query().order_by(Technology.display_order.asc(), Technology.name.asc()))

    async def add(self, technology: Technology) -> Technology:
        self.session.add(technology)
        await self.session.flush()
        return technology

    async def update(self, technology: Technology) -> Technology:
        await self.session.flush()
        return technology
