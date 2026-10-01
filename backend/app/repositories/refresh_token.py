from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        return await self.session.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))

    async def add(self, token: RefreshToken) -> RefreshToken:
        self.session.add(token)
        await self.session.flush()
        return token

    async def revoke(self, token: RefreshToken, replacement_id=None) -> None:
        token.revoked_at = datetime.now(timezone.utc)
        token.replaced_by_token_id = replacement_id
        await self.session.flush()
