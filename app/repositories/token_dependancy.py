from abc import ABC, abstractmethod
from uuid import UUID
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from utility.hash_token import hash_refresh_token
from models.models import RefreshToken


class ITokenRepository(ABC):
    @abstractmethod
    async def save(
        self, user_id: UUID, token: str, expires_at: datetime
    ):
        pass

    @abstractmethod
    async def revoke_token(self, user_id: UUID):
        pass


class TokenRepository(ITokenRepository):
    def __init__(self, db: AsyncSession):
        self._db_session = db

    async def save(
        self, user_id: UUID, token: str, expires_at: datetime
    ):
        refresh = RefreshToken(
            user_id=user_id,
            token=hash_refresh_token(token),
            expires_at=expires_at,
        )
        self._db_session.add(refresh)
        await self._db_session.flush()

    async def revoke_token(self, user_id: UUID):
        await self._db_session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await self._db_session.flush()
