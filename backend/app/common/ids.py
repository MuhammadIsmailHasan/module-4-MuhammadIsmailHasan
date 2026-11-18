import uuid


def to_uuid(value):
    """Return a UUID or None when the value is not a valid UUID."""
    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError):
        return None
