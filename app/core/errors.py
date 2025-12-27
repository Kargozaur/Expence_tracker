class InvalidTokenError(Exception):
    pass


class UserDoesntExist(Exception):
    pass


class WrongCredentials(Exception):
    pass


class UserAlreadyExists(Exception):
    pass


class ExpenseDoesNotExists(Exception):
    pass


class ExpensesDoesNotExist(Exception):
    pass


class CurrencyDoesNotExists(Exception):
    pass


class CategoryDoesNotExists(Exception):
    pass
