from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import Media


class MediaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _base_query(self) -> Select[tuple[Media]]:
        return select(Media)

    async def get_by_id(self, media_id: UUID) -> Media | None:
        return await self.session.scalar(self._base_query().where(Media.id == media_id))

    async def get_by_storage_key(self, storage_key: str) -> Media | None:
        return await self.session.scalar(self._base_query().where(Media.storage_key == storage_key))

    async def add(self, media: Media) -> Media:
        self.session.add(media)
        await self.session.flush()
        return media

    async def update(self, media: Media) -> Media:
        await self.session.flush()
        return media
