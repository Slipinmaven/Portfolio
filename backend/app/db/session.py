from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings


def create_engine(settings: Settings) -> AsyncEngine:
    kwargs = {"echo": settings.db_echo, "pool_pre_ping": settings.db_pool_pre_ping, "pool_recycle": settings.db_pool_recycle}
    if settings.database_url.startswith("sqlite"):
        return create_async_engine(settings.database_url, **kwargs)
    return create_async_engine(settings.database_url, pool_size=settings.db_pool_size, max_overflow=settings.db_max_overflow, pool_timeout=settings.db_pool_timeout, **kwargs)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def session_from_factory(factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncSession]:
    async with factory() as session:
        yield session
