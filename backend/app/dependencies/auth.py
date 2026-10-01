from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.dependencies.database import get_db_session
from app.models.user import User
from app.repositories.user import UserRepository

bearer = HTTPBearer(auto_error=False)


async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)], session: Annotated[AsyncSession, Depends(get_db_session)]) -> User:
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if not credentials:
        raise unauthorized
    try:
        payload = decode_access_token(credentials.credentials, get_settings())
        if payload.get("type") != "access":
            raise ValueError
        user_id = UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise unauthorized from None
    user = await UserRepository(session).get_by_id(user_id)
    if not user or not user.is_active:
        raise unauthorized
    return user


async def require_authenticated_user(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user


async def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
