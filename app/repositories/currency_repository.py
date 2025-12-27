from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.models import Currency


class ICurrencyRepository(ABC):
    @abstractmethod
    async def get_all(self):
        pass


class CurrencyRepository:
    def __init__(self, db: AsyncSession):
        self._db_session = db

    async def get_all(self):
        query = select(Currency.code, Currency.id)
        result = await self._db_session.execute(query)
        return result.mappings().all()
