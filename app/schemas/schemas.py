from enum import Enum


class BaseEnum(Enum, str):
    pass


class ExpensesCategory(BaseEnum):
    Cafe = "Cafe"
    Groceries = "Groceries"
    Construction_materials = "Construction materials"
    Clothes = "Clothes"
    Health = "Health"
    Taxi = "Taxi"
    Other = "Other"
