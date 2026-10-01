from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.dependencies.database import get_db_session
from app.repositories.health import HealthRepository
from app.repositories.media import MediaRepository
from app.repositories.project import ProjectRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.technology import TechnologyRepository
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.services.health import HealthService
from app.services.project import ProjectService, TechnologyService


def get_project_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> ProjectService:
    return ProjectService(ProjectRepository(session), TechnologyRepository(session), MediaRepository(session))


def get_technology_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> TechnologyService:
    return TechnologyService(TechnologyRepository(session))


def get_auth_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> AuthService:
    return AuthService(UserRepository(session), RefreshTokenRepository(session), get_settings())


def get_health_service(session: Annotated[AsyncSession, Depends(get_db_session)]) -> HealthService:
    return HealthService(HealthRepository(session))