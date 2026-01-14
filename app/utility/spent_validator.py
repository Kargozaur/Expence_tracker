from decimal import Decimal


def is_positive(value: Decimal) -> Decimal:
    return value < 0
