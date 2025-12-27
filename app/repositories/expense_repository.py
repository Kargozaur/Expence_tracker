from sqlalchemy.ext.asyncio import AsyncSession
from abc import ABC, abstractmethod
import uuid
from sqlalchemy import (
    select,
    update,
    extract,
    outerjoin,
    Select,
    delete,
)
from models.models import Expenses, Category, Currency
from schemas.schemas import (
    GetExpenses,
    PaginationParams,
    UpdateExpense,
)


class IExpenseRepository(ABC):
    @abstractmethod
    async def get_user_expenses(
        self, user_id: uuid.UUID, pagination: PaginationParams
    ):
        pass

    @abstractmethod
    async def get_expense_by_category(
        self,
        user_id: uuid.UUID,
        category: str,
        pagination: PaginationParams,
    ):
        pass

    @abstractmethod
    async def get_expense_by_id(
        self, user_id: uuid.UUID, expense_id: int
    ):
        pass

    @abstractmethod
    async def create_expense(self, expense_data: Expenses):
        pass

    @abstractmethod
    async def change_expense(
        self,
        user_id: uuid.UUID,
        expense_id: int,
        new_data: dict,
    ):
        pass

    @abstractmethod
    async def delete_expense(self, user_id: uuid.UUID, expense_id):
        pass


class ExpenseRepository(IExpenseRepository):
    """CRUD realization here. Sync methods are for queries, as they do not interfere
    into I/O, so they may be sync. Later, probably, it is better to make another class
    for the queries and use them as some sort of DI.
    """

    def __init__(self, db: AsyncSession):
        self._db_session = db

    def get_expense(self) -> Select:
        return select(Expenses)

    def base_expense_query(self) -> Select:
        return (
            select(
                Expenses.id,
                Category.category_name,
                Expenses.amount,
                Currency.symbol.label("currency_code"),
                Expenses.note,
                extract("year", Expenses.expense_date).label("year"),
                extract("month", Expenses.expense_date).label(
                    "month"
                ),
                extract("day", Expenses.expense_date).label("day"),
            )
            .join(Expenses.currencies)
            .outerjoin(Expenses.categories)
        )

    def _for_user(self, query: Select, user_id: uuid.UUID) -> Select:
        return query.where(Expenses.user_id == user_id)

    def _by_category_name(
        self, query: Select, category: str
    ) -> Select:
        return query.where(Category.category_name == category)

    def _by_expense_id_and_user(
        self, query: Select, user_id: uuid.UUID, expense_id: int
    ):
        return query.where(
            Expenses.id == expense_id, Expenses.user_id == user_id
        )

    def _paginated(
        self, query: Select, limit: int, offset: int
    ) -> Select:
        return query.limit(limit).offset(offset)

    def _ordered_by_date_desc(self, query: Select) -> Select:
        return query.order_by(Expenses.expense_date.desc())

    async def get_user_expenses(
        self, user_id: uuid.UUID, pagination: PaginationParams
    ) -> list[GetExpenses]:
        query = self.base_expense_query()
        query = self._for_user(query, user_id)
        query = self._ordered_by_date_desc(query)
        query = self._paginated(
            query, pagination.limit, pagination.offset
        )
        result = await self._db_session.execute(query)
        rows = result.mappings().all()
        if not rows:
            return []
        return [GetExpenses.model_validate(row) for row in rows]

    async def get_expense_by_id(
        self, user_id: uuid.UUID, expense_id: int
    ) -> GetExpenses | None:
        query = self.base_expense_query()
        query = self._for_user(query, user_id)
        query = query.where(Expenses.id == expense_id)
        result = await self._db_session.execute(query)
        row = result.mappings().first()
        return GetExpenses.model_validate(row) if row else None

    async def get_expense_by_category(
        self,
        user_id: uuid.UUID,
        category: str,
        pagination: PaginationParams,
    ) -> list[GetExpenses]:
        query = self.base_expense_query()
        query = self._for_user(query, user_id)
        query = self._by_category_name(query, category)
        query = self._ordered_by_date_desc(query)
        query = self._paginated(
            query, pagination.limit, pagination.offset
        )
        result = await self._db_session.execute(query)
        rows = result.mappings().all()
        if not rows:
            return []
        return [GetExpenses.model_validate(row) for row in rows]

    async def create_expense(self, expense_data: Expenses):
        self._db_session.add(expense_data)
        await self._db_session.flush()

        query = self.base_expense_query().where(
            Expenses.id == expense_data.id
        )
        result = await self._db_session.execute(query)
        row = result.mappings().first()
        return row

    async def delete_expense(
        self, user_id: uuid.UUID, expense_id: int
    ):
        query = delete(Expenses).where(
            Expenses.id == expense_id, Expenses.user_id == user_id
        )
        result = await self._db_session.execute(query)
        return result.rowcount > 0

    async def change_expense(
        self,
        user_id: uuid.UUID,
        expense_id: int,
        new_data: dict,
    ) -> bool:
        """
        Returns True if row was found and updated
        Returns False otherwise
        """
        query = (
            update(Expenses)
            .values(**new_data)
            .where(
                Expenses.user_id == user_id, Expenses.id == expense_id
            )
        )
        result = await self._db_session.execute(query)
        return result.rowcount
