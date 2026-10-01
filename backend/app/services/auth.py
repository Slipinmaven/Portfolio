from datetime import datetime, timedelta, timezone

from app.core.config import Settings
from app.core.exceptions import AuthenticationError, TokenReuseError
from app.core.security import create_access_token, generate_refresh_token, hash_refresh_token, verify_password
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository, token_repo: RefreshTokenRepository, settings: Settings):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.settings = settings

    async def login(self, email: str, password: str, ip: str | None, user_agent: str | None):
        user = await self.user_repo.get_by_email(email.lower())
        if not user or not user.is_active or not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password")
        user.last_login_at = datetime.now(timezone.utc)
        tokens = await self._issue_tokens(user, ip, user_agent)
        await self.user_repo.session.commit()
        return tokens

    async def refresh(self, raw_token: str, ip: str | None, user_agent: str | None):
        token = await self.token_repo.get_by_hash(hash_refresh_token(raw_token))
        now = datetime.now(timezone.utc)
        if not token or token.expires_at <= now:
            raise AuthenticationError("Invalid or expired refresh token")
        if token.revoked_at is not None:
            raise TokenReuseError("Refresh token has already been revoked")
        user = await self.user_repo.get_by_id(token.user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User is inactive")
        access_token, refresh_token, replacement = await self._issue_tokens(user, ip, user_agent)
        await self.token_repo.revoke(token, replacement.id)
        await self.user_repo.session.commit()
        return access_token, refresh_token

    async def logout(self, raw_token: str) -> None:
        token = await self.token_repo.get_by_hash(hash_refresh_token(raw_token))
        if token and token.revoked_at is None:
            await self.token_repo.revoke(token)
        await self.token_repo.session.commit()

    async def _issue_tokens(self, user: User, ip: str | None, user_agent: str | None):
        raw_refresh = generate_refresh_token()
        refresh = RefreshToken(user_id=user.id, token_hash=hash_refresh_token(raw_refresh), expires_at=datetime.now(timezone.utc) + timedelta(days=self.settings.refresh_token_expire_days), created_by_ip=ip, user_agent=user_agent)
        await self.token_repo.add(refresh)
        return create_access_token(str(user.id), self.settings), raw_refresh, refresh
