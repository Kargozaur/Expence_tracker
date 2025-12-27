from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.models import Currency


class ICurrencyRepository(ABC):
    @abstractmethod
    async def get_id_by_code(self, code: str):
        pass


class CurrencyRepository:
    def __init__(self, db: AsyncSession):
        self._db_session = db

    async def get_id_by_code(self, code: str) -> Currency | None:
        query = select(Currency).where(Currency.code == code)
        result = await self._db_session.execute(query)
        return result.scalar_one_or_none()
