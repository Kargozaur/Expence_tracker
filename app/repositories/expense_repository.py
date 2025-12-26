from abc import ABC, abstractmethod
import uuid


class IExpenseRepository(ABC):
    @abstractmethod
    async def get_all_expenses_for_user(id: uuid.UUID):
        pass

    @abstractmethod
    async def get_expense_by_category(category: str):
        pass

    @abstractmethod
    async def create_expense(expense_id: int):
        pass

    @abstractmethod
    async def change_expense(expense_id: int):
        pass

    @abstractmethod
    async def delete_expense(expense_id):
        pass
