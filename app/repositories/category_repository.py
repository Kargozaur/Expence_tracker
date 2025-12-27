from sqlalchemy.ext.asyncio import AsyncSession
from abc import ABC, abstractmethod
from sqlalchemy import select
from models.models import Category


class ICategoryRepository(ABC):
    @abstractmethod
    async def get_category_by_id(
        self, category_name: str
    ) -> Category | None:
        pass


class CategoryRepository(ICategoryRepository):
    def __init__(self, db: AsyncSession):
        self._db_session = db

    async def get_category_by_id(
        self, category_name
    ) -> Category | None:
        query = select(Category).where(
            Category.category_name == category_name
        )
        result = await self._db_session.execute(query)
        return result.scalar_one_or_none()
