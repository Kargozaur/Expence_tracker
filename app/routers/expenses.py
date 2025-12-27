from fastapi.openapi.utils import status_code_ranges
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Response,
)
from services.expense_service import ExpenseService
from schemas.schemas import CreateExpense, GetExpenses, UpdateExpense
from dependancies.expenses.expenses_router_dependancy import (
    get_expense_service,
)
from dependancies.pagination.pagination_dependancy import (
    PaginationDep,
)
from core.errors import (
    CategoryDoesNotExists,
    CurrencyDoesNotExists,
)
from auth.oauth import get_current_user

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/", response_model=GetExpenses)
async def create_expense(
    expense_in: CreateExpense,
    expense_service: ExpenseService = Depends(get_expense_service),
    current_user=Depends(get_current_user),
):
    try:
        new_expense = await expense_service.create_expense(
            current_user.id, expense_in
        )
        return new_expense
    except CategoryDoesNotExists:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Category not supported",
        )
    except CurrencyDoesNotExists:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Currency not supported",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occured",
        )


@router.get(
    "/",
    response_model=list[GetExpenses],
    status_code=status.HTTP_200_OK,
)
async def get_all_expenses(
    pagination: PaginationDep,
    expense_service: ExpenseService = Depends(get_expense_service),
    current_user=Depends(get_current_user),
):
    expenses = await expense_service.get_all_expenses(
        current_user.id, pagination
    )
    return expenses


@router.get(
    "/{id}",
    response_model=GetExpenses,
    status_code=status.HTTP_200_OK,
)
async def get_expense_by_id(
    id: int,
    expense_service: ExpenseService = Depends(get_expense_service),
    current_user=Depends(get_current_user),
):
    expense = await expense_service.get_expense_by_id(
        current_user.id, id
    )
    return expense


@router.get(
    "/{category_name}",
    response_model=list[GetExpenses],
    status_code=status.HTTP_200_OK,
)
async def get_expenses_by_category(
    category_name: str,
    pagination: PaginationDep,
    expense_service: ExpenseService = Depends(get_expense_service),
    current_user=Depends(get_current_user),
):
    expenses = await expense_service.get_expense_by_category(
        current_user.id, category_name, pagination
    )
    return expenses


@router.patch(
    "/{id}",
    status_code=status.HTTP_206_PARTIAL_CONTENT,
    response_model=GetExpenses,
)
async def update_expense(
    id: int,
    user_data: UpdateExpense,
    expense_service: ExpenseService = Depends(get_expense_service),
    current_user=Depends(get_current_user),
):
    try:
        new_expense = await expense_service.update_expense(
            current_user.id, id, user_data
        )
        return new_expense
    except CategoryDoesNotExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category is not supported",
        )
    except CurrencyDoesNotExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Currency is not supported",
        )


@router.delete(
    "/{expense_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_expense(
    expense_id: int,
    expense_service: ExpenseService = Depends(get_expense_service),
    current_user=Depends(get_current_user),
):
    await expense_service.delete_expense(current_user.id, expense_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
