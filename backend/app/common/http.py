from datetime import date

from flask import request

from app.common.errors import ValidationError


def json_body():
    data = request.get_json(silent=True)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValidationError("Body must be a JSON object")
    return data


def parse_date(value, field):
    if value is None:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        raise ValidationError(f"{field} must be an ISO date (YYYY-MM-DD)")


def iso(value):
    return value.isoformat() if value is not None else None
