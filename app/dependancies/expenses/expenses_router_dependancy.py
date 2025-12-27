from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from services.expense_service import ExpenseService
from database import get_db
from repositories.category_repository import CategoryRepository
from repositories.currency_repository import CurrencyRepository
from repositories.expense_repository import ExpenseRepository


async def get_category_repo(db: AsyncSession = Depends(get_db)):
    return CategoryRepository(db)


async def get_currency_repo(db: AsyncSession = Depends(get_db)):
    return CurrencyRepository(db)


async def get_expense_repo(db: AsyncSession = Depends(get_db)):
    return ExpenseRepository(db)


async def get_expense_service(
    db: AsyncSession = Depends(get_db),
    category_repo=Depends(get_category_repo),
    currency_repo=Depends(get_currency_repo),
    expense_repo=Depends(get_expense_repo),
):
    from main import app

    return ExpenseService(
        db,
        category_repo,
        currency_repo,
        expense_repo,
        app.state.currency_map,
        app.state.category_map,
    )
