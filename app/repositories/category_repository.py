from sqlalchemy.ext.asyncio import AsyncSession
from abc import ABC, abstractmethod
from sqlalchemy import select
from models.models import Category


class ICategoryRepository(ABC):
    @abstractmethod
    async def get_all(self):
        pass


class CategoryRepository(ICategoryRepository):
    def __init__(self, db: AsyncSession):
        self._db_session = db

    async def get_all(
        self,
    ):
        query = select(Category)
        result = await self._db_session.execute(query)
        return result.scalars().all()
