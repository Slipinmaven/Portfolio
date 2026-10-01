import asyncio
import getpass
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import create_engine, create_session_factory
from app.models.user import User
from app.repositories.user import UserRepository


async def create_admin() -> None:
    settings = get_settings()
    email = (os.getenv("BOOTSTRAP_ADMIN_EMAIL") or input("Admin email: ")).strip().lower()
    password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD") or getpass.getpass("Admin password: ")
    if len(password) < 12:
        raise ValueError("Admin password must contain at least 12 characters")
    engine = create_engine(settings)
    factory = create_session_factory(engine)
    async with factory() as session:
        repo = UserRepository(session)
        if await repo.get_by_email(email):
            raise ValueError("An account with that email already exists")
        await repo.add(User(email=email, password_hash=hash_password(password), role="admin", email_verified_at=datetime.now(timezone.utc)))
        await session.commit()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin())
