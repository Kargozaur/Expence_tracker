from datetime import datetime, timezone
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import User, RefreshToken
import uuid


async def get_user(email: str, db: AsyncSession):
    query: Result[tuple[User]] = await db.execute(
        select(User).where(User.email == email)
    )
    result: User | None = query.scalar_one_or_none()
    return result


async def has_token(
    id: uuid.UUID, db: AsyncSession
) -> RefreshToken | None:
    now = datetime.now(timezone.utc)
    query: Result[tuple[RefreshToken]] = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == id,
            RefreshToken.expires_at > now,
            RefreshToken.revoked_at.is_(None),
        )
    )
    result: RefreshToken | None = query.scalar_one_or_none()
    return result
