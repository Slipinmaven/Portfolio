from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.exceptions import ProjectConflictError, ProjectValidationError, TechnologyNotFoundError
from app.dependencies.auth import require_admin
from app.dependencies.services import get_project_service
from app.schemas.project import ProjectAdminResponse, ProjectCreate, ProjectPublicResponse, ProjectUpdate
from app.services.project import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])
ProjectServiceDependency = Annotated[ProjectService, Depends(get_project_service)]


@router.get("", response_model=list[ProjectPublicResponse])
async def list_public_projects(service: ProjectServiceDependency):
    projects = await service.list_public_projects()
    return [ProjectPublicResponse.model_validate(project) for project in projects]


@router.get("/admin", response_model=list[ProjectAdminResponse])
async def list_admin_projects(service: ProjectServiceDependency, admin=Depends(require_admin)):
    projects = await service.list_admin_projects()
    return [ProjectAdminResponse.model_validate(project) for project in projects]


@router.post("", response_model=ProjectAdminResponse, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, service: ProjectServiceDependency, admin=Depends(require_admin)):
    try:
        project = await service.create_project(payload)
    except ProjectConflictError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    except (ProjectValidationError, TechnologyNotFoundError) as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return ProjectAdminResponse.model_validate(project)


@router.get("/admin/{project_id}", response_model=ProjectAdminResponse)
async def get_admin_project(project_id: UUID, service: ProjectServiceDependency, admin=Depends(require_admin)):
    project = await service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectAdminResponse.model_validate(project)


@router.patch("/admin/{project_id}", response_model=ProjectAdminResponse)
async def update_project(project_id: UUID, payload: ProjectUpdate, service: ProjectServiceDependency, admin=Depends(require_admin)):
    project = await service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    try:
        project = await service.update_project(project, payload)
    except ProjectConflictError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    except ProjectValidationError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return ProjectAdminResponse.model_validate(project)


@router.post("/admin/{project_id}/publish", response_model=ProjectAdminResponse)
async def publish_project(project_id: UUID, service: ProjectServiceDependency, admin=Depends(require_admin)):
    project = await service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectAdminResponse.model_validate(await service.publish(project))


@router.post("/admin/{project_id}/unpublish", response_model=ProjectAdminResponse)
async def unpublish_project(project_id: UUID, service: ProjectServiceDependency, admin=Depends(require_admin)):
    project = await service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectAdminResponse.model_validate(await service.unpublish(project))


@router.get("/{slug}", response_model=ProjectPublicResponse)
async def get_public_project(slug: str, service: ProjectServiceDependency):
    project = await service.get_project_by_slug(slug)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectPublicResponse.model_validate(project)
