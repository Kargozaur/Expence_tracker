from datetime import datetime


def validate_date(date: datetime) -> datetime:
    if date > datetime.now():
        raise ValueError("Date can't be in the future")
    return date
