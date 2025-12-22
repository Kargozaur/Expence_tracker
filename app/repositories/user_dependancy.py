from abc import ABC, abstractmethod
from datetime import datetime, timezone
from sqlalchemy import Result, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import User, RefreshToken
import uuid


class IUserRepository(ABC):
    @abstractmethod
    async def get_user_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def add_user(self, user: User) -> User:
        pass

    @abstractmethod
    async def has_token(self, id: uuid.UUID) -> RefreshToken | None:
        pass

    @abstractmethod
    async def revoke_token(self, id: uuid.UUID) -> None:
        pass


class UserRepository(IUserRepository):
    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def get_user_by_email(self, email: str) -> User | None:
        query: Result[tuple[User]] = await self._db_session.execute(
            select(User).where(User.email == email)
        )
        result: User | None = query.scalar_one_or_none()
        return result

    async def add_user(self, user: User) -> User:
        self._db_session.add(user)
        await self._db_session.flush()
        return user

    async def has_token(self, id: uuid.UUID) -> RefreshToken | None:
        now = datetime.now(timezone.utc)
        query: Result[
            tuple[RefreshToken]
        ] = await self._db_session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == id,
                RefreshToken.expires_at > now,
                RefreshToken.revoked_at.is_(None),
            )
        )
        result: RefreshToken | None = query.scalar_one_or_none()
        return result

    async def revoke_token(self, id: uuid.UUID) -> None:
        await self._db_session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(timezone.utc))
        )
