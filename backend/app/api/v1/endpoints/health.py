from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.services import get_health_service
from app.services.health import HealthService

router = APIRouter(tags=["health"])
HealthServiceDependency = Annotated[HealthService, Depends(get_health_service)]


@router.get("/health")
async def health(service: HealthServiceDependency):
    return await service.check()
