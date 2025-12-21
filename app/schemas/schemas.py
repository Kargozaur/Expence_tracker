from datetime import datetime
import re
from enum import Enum
from typing import Optional
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    ValidationError,
)
from pydantic_settings import SettingsConfigDict


# class BaseEnum(Enum, str):
#     pass


# class ExpensesCategory(BaseEnum):
#     Cafe = "Cafe"
#     Groceries = "Groceries"
#     Construction_materials = "Construction materials"
#     Clothes = "Clothes"
#     Health = "Health"
#     Taxi = "Taxi"
#     Other = "Other"


# class Currency(BaseEnum):
#     uah = "₴"
#     euro = "€"
#     usd = "$"


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


# class CreateExpense(BaseModel):
#     category: ExpensesCategory
#     currency: Currency
#     amount: int | float
#     note: Optional[str] = None
#     expense_date: datetime


class GetExpenses(BaseModel):
    category: str
    currency: str
    amount: int | float
    note: str
    expense_date: datetime

    model_config = SettingsConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: int | None = None
    exp: int | None = None
