from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.exceptions import ProjectValidationError, TechnologyConflictError
from app.dependencies.auth import require_admin
from app.dependencies.services import get_technology_service
from app.schemas.project import TechnologyCreate, TechnologyResponse, TechnologyUpdate
from app.services.project import TechnologyService

router = APIRouter(prefix="/technologies", tags=["technologies"])
TechnologyServiceDependency = Annotated[TechnologyService, Depends(get_technology_service)]


@router.get("", response_model=list[TechnologyResponse])
async def list_technologies(service: TechnologyServiceDependency):
    technologies = await service.list_technologies()
    return [TechnologyResponse.model_validate(technology) for technology in technologies]


@router.get("/admin", response_model=list[TechnologyResponse])
async def list_admin_technologies(service: TechnologyServiceDependency, admin=Depends(require_admin)):
    technologies = await service.list_technologies()
    return [TechnologyResponse.model_validate(technology) for technology in technologies]


@router.post("", response_model=TechnologyResponse, status_code=status.HTTP_201_CREATED)
async def create_technology(payload: TechnologyCreate, service: TechnologyServiceDependency, admin=Depends(require_admin)):
    try:
        technology = await service.create_technology(payload)
    except TechnologyConflictError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    except ProjectValidationError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return TechnologyResponse.model_validate(technology)


@router.get("/admin/{technology_id}", response_model=TechnologyResponse)
async def get_admin_technology(technology_id: UUID, service: TechnologyServiceDependency, admin=Depends(require_admin)):
    technology = await service.get_by_id(technology_id)
    if not technology:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technology not found")
    return TechnologyResponse.model_validate(technology)


@router.patch("/admin/{technology_id}", response_model=TechnologyResponse)
async def update_technology(technology_id: UUID, payload: TechnologyUpdate, service: TechnologyServiceDependency, admin=Depends(require_admin)):
    technology = await service.get_by_id(technology_id)
    if not technology:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technology not found")
    try:
        technology = await service.update_technology(technology, payload)
    except TechnologyConflictError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    return TechnologyResponse.model_validate(technology)


@router.get("/{slug}", response_model=TechnologyResponse)
async def get_technology(slug: str, service: TechnologyServiceDependency):
    technology = await service.get_by_slug(slug)
    if not technology:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technology not found")
    return TechnologyResponse.model_validate(technology)
