from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.exceptions import AuthenticationError, TokenReuseError
from app.dependencies.auth import require_authenticated_user
from app.dependencies.services import get_auth_service
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
AuthServiceDependency = Annotated[AuthService, Depends(get_auth_service)]


def request_metadata(request: Request) -> tuple[str | None, str | None]:
    return request.client.host if request.client else None, request.headers.get("user-agent")


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, request: Request, service: AuthServiceDependency):
    ip, user_agent = request_metadata(request)
    try:
        tokens = await service.login(str(payload.email), payload.password, ip, user_agent)
    except AuthenticationError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from None
    return TokenResponse(access_token=tokens[0], refresh_token=tokens[1])


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, request: Request, service: AuthServiceDependency):
    ip, user_agent = request_metadata(request)
    try:
        tokens = await service.refresh(payload.refresh_token, ip, user_agent)
    except TokenReuseError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token reuse detected") from None
    except AuthenticationError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from None
    return TokenResponse(access_token=tokens[0], refresh_token=tokens[1])


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshRequest, service: AuthServiceDependency):
    await service.logout(payload.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(user: Annotated[User, Depends(require_authenticated_user)]):
    return user
