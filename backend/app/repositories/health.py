from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class HealthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_database(self) -> bool:
        try:
            await self.session.execute(text("SELECT 1"))
        except Exception:
            return False
        return True