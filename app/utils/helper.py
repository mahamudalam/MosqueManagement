from datetime import datetime


def format_date(value):
    if not value:
        return ""
    if isinstance(value, str):
        return value
    return value.strftime("%Y-%m-%d")


def current_year():
    return datetime.today().year
