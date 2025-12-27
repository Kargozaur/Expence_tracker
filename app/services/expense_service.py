import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Expenses
from repositories.category_repository import ICategoryRepository
from repositories.currency_repository import ICurrencyRepository
from repositories.expense_repository import IExpenseRepository
from schemas.schemas import (
    CreateExpense,
    PaginationParams,
    UpdateExpense,
    GetExpenses,
)
from core.errors import (
    CategoryDoesNotExists,
    CurrencyDoesNotExists,
    ExpenseDoesNotExists,
)


class ExpenseService:
    """
    Expense repo methods:
        get_user_expenses(user_id, pagination)
        get_expense_by_category(user_id, category, pagination)
        get_expense_by_id(user_id, expense_id)
        create_expense(expense_data)
        change_expense(user_id, expense_id, new_data)
        delete_expense(user_id, expense_id)
    """

    def __init__(
        self,
        db_session: AsyncSession,
        category_repo: ICategoryRepository,
        currency_repo: ICurrencyRepository,
        expense_repo: IExpenseRepository,
        currency_map: dict[str, int],
        category_map: dict[str, int],
    ):
        self._db_session = db_session
        self.category_repo = category_repo
        self.currency_repo = currency_repo
        self.expense_repo = expense_repo
        self.currency_map: dict[str, int] = currency_map
        self.category_map: dict[str, int] = category_map

    async def create_expense(
        self, user_id: uuid.UUID, user_data: CreateExpense
    ) -> GetExpenses:
        currency_id: int | None = self.currency_map[
            user_data.currency.value
        ]
        if not currency_id:
            raise CurrencyDoesNotExists(
                f"Currency {user_data.currency} is not supported"
            )

        category_id: int | None = self.category_map[
            user_data.category.value
        ]
        if not category_id:
            raise CategoryDoesNotExists(
                f"Category {user_data.category} is not supported"
            )

        expense = Expenses(
            user_id=user_id,
            category_id=category_id,
            currency_id=currency_id,
            amount=user_data.amount,
            note=user_data.note,
            expense_date=user_data.expense_date,
        )

        new_expense = await self.expense_repo.create_expense(expense)
        return GetExpenses.model_validate(new_expense)

    async def get_expense_by_id(
        self, user_id: uuid.UUID, expense_id: int
    ) -> GetExpenses:
        expense = await self.expense_repo.get_expense_by_id(
            user_id, expense_id
        )

        if not expense:
            raise ExpenseDoesNotExists
        return expense

    async def get_expense_by_category(
        self,
        user_id: uuid.UUID,
        category: str,
        pagination: PaginationParams,
    ) -> list[GetExpenses]:
        expenses = await self.expense_repo.get_expense_by_category(
            user_id, category, pagination
        )

        return expenses

    async def get_all_expenses(
        self, user_id: uuid.UUID, pagination: PaginationParams
    ) -> list[GetExpenses]:
        expenses = await self.expense_repo.get_user_expenses(
            user_id, pagination
        )
        return expenses

    async def delete_expense(
        self, user_id: uuid.UUID, expense_id: int
    ):
        deleted = await self.expense_repo.delete_expense(
            user_id, expense_id
        )
        if not deleted:
            raise ExpenseDoesNotExists(
                f"Expense with id {expense_id} doesn't exists or not owned"
            )

    async def update_expense(
        self,
        user_id: uuid.UUID,
        expense_id: int,
        user_data: UpdateExpense,
    ) -> GetExpenses:
        update_data = user_data.model_dump(exclude_unset=True)
        if "category_name" in update_data:
            category_id: int | None = self.category_map.get(
                update_data["category_name"]
            )
            if not category_id:
                raise CategoryDoesNotExists(
                    f"Category {update_data['category_name']} is not supported"
                )
            update_data["category_id"] = category_id
            del update_data["category_name"]
        if "currency_code" in update_data:
            currency_id: int | None = self.currency_map.get(
                update_data["currency_code"]
            )
            if not currency_id:
                raise CurrencyDoesNotExists(
                    f"Currency {update_data['currency_name']} is not supported"
                )
            update_data["currency_id"] = currency_id
            del update_data["currency_code"]
        expense = await self.expense_repo.change_expense(
            user_id, expense_id, update_data
        )
        if not expense:
            raise ExpenseDoesNotExists(
                f"Expense {expense_id} not found or not owned"
            )
        fresh = await self.expense_repo.get_expense_by_id(
            user_id, expense_id
        )
        return GetExpenses.model_validate(fresh)
