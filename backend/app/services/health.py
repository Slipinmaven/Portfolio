from app.repositories.health import HealthRepository


class HealthService:
    def __init__(self, repository: HealthRepository):
        self.repository = repository

    async def check(self) -> dict[str, str]:
        database = "healthy" if await self.repository.check_database() else "unhealthy"
        return {"status": "healthy" if database == "healthy" else "unhealthy", "database": database}