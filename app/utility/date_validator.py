from datetime import date


def validate_date(date_to_check: date) -> date:
    if date_to_check > date.today():
        raise ValueError("Date can't be in the future")
    return date_to_check
