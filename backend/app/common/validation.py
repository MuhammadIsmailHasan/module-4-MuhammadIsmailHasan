"""Identity validation shared by register, login, profile and candidate search (V10, Decisions M and N)."""
import re

from app.common.errors import ValidationError

USERNAME_RE = re.compile(r"^[a-z0-9_.]{3,30}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$")
EMAIL_MAX = 255


def normalize_username(raw):
    return raw.strip().lower()


def normalize_email(raw):
    return raw.strip().lower()


def is_username(value):
    return USERNAME_RE.fullmatch(value) is not None


def is_email_shape(value):
    """One "@", a local part, a dotted domain, no spaces, at most 255 characters."""
    return len(value) <= EMAIL_MAX and _EMAIL_RE.fullmatch(value) is not None


def classify_identifier(raw):
    """Return ("email", value) or ("username", value); raise ValidationError (details.identifier) otherwise."""
    value = raw.strip().lower()
    if "@" in value:
        if is_email_shape(value):
            return "email", value
    elif is_username(value):
        return "username", value
    raise ValidationError(
        "Enter a valid username or email", details={"identifier": ["Enter a valid username or email"]}
    )
