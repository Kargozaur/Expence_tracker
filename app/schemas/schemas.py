from datetime import date
import re
from enum import StrEnum
from typing import Optional, Annotated
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    ConfigDict,
    AfterValidator,
)
import uuid
from utility.spent_validator import is_positive
from utility.date_validator import validate_date
from decimal import Decimal

CheckExpense = Annotated[Decimal, AfterValidator(is_positive)]
NotInFuture = Annotated[date, AfterValidator(validate_date)]


class ExpensesCategory(StrEnum):
    """
    ('Food & Groceries'),
    ('Transportation'),
    ('Housing & Utilities'),
    ('Entertainment'),
    ('Health'),
    ('Education'),
    ('Shopping'),
    ('Travel'),
    ('Other')

    """

    Food_and_Groceries = "Food & Groceries"
    Transport = "Transportation"
    Housing_and_utilities = "Housing & Utilities"
    Health = "Health"
    Education = "Education"
    Shopping = "Shopping"
    Travel = "Travel"
    Other = "Other"


class Currency(StrEnum):
    """
    ('USD', 'US Dollar')
    ('EUR', 'Euro')
    ('GBP', 'British Pound')
    ('UAH', 'Ukrainian Hryvnia)
    ('PLN', 'Polish Złoty')
    ('JPY', 'Japanese Yen')
    ('CAD', 'Canadian Dollar')
    ('CHF', 'Swiss Franc')
    """

    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    UAH = "UAH"
    PLN = "PLN"
    JPY = "JPY"
    CAD = "CAD"
    CHF = "CHF"


class CreateUser(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def verify_password(cls, value: str) -> str:
        if not re.search(r"[A-Z]", value):
            raise ValueError("password.uppercase_required")
        if not re.search(r"\d", value):
            raise ValueError("password.number_required")
        if not re.search(r"[!@#$%^&*(),.:<>|?]", value):
            raise ValueError("password.specialsymbol_required")
        return value


class LoginUser(BaseModel):
    email: str
    password: str


class CreateExpense(BaseModel):
    category: ExpensesCategory
    currency: Currency
    amount: CheckExpense = Field(..., gt=0)
    note: Optional[str] = None
    expense_date: NotInFuture


class GetExpenses(BaseModel):
    id: int
    category_name: str
    currency_code: str
    amount: float
    note: str | None
    year: int
    month: int
    day: int

    model_config = ConfigDict(from_attributes=True)


class UpdateExpense(BaseModel):
    category_name: Optional[ExpensesCategory] = None
    currency_code: Optional[Currency] = None
    amount: Optional[CheckExpense] = None
    expense_date: Optional[NotInFuture] = None
    note: Optional[str] = ""


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: uuid.UUID | None = None
    exp: int | None = None


class PaginationParams(BaseModel):
    limit: int = Field(30, ge=1, le=50)
    offset: int = Field(0, le=50)
