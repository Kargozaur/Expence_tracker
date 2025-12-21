from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import User


async def get_user(email: str, db: AsyncSession):
    query: Result[tuple[User]] = await db.execute(
        select(User).where(User.email == email)
    )
    result: User | None = query.scalar_one_or_none()
    return result
