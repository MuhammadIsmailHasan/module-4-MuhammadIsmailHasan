from app.common.errors import ValidationError


def _text(data, key, label):
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} is required")
    return value.strip()


def validate_register(data):
    full_name = _text(data, "full_name", "full_name")
    login = _text(data, "login_identifier", "login_identifier")
    if len(login) > 255:
        raise ValidationError("login_identifier must be at most 255 characters")
    password = data.get("password")
    if not isinstance(password, str) or len(password) < 8:
        raise ValidationError("password must be at least 8 characters")
    return full_name, login, password


def validate_login(data):
    login = _text(data, "login_identifier", "login_identifier")
    password = data.get("password")
    if not isinstance(password, str) or not password:
        raise ValidationError("password is required")
    return login, password


def serialize_user(user):
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "login_identifier": user.login_identifier,
        "avatar_url": user.avatar_url,
    }


def serialize_user_admin(user):
    return {**serialize_user(user), "role": user.role}
