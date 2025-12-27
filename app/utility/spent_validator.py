from decimal import Decimal


def is_positive(value: Decimal) -> Decimal:
    if value < 0:  # ty:ignore[unsupported-operator]
        raise ValueError("Value has to be positive")
    return value
