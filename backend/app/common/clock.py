"""Injectable clock so time-dependent logic is testable."""
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

_now_override = None


def set_now(value):
    """Tests: pass a callable returning an aware datetime, or None to reset."""
    global _now_override
    _now_override = value


def now() -> datetime:
    if _now_override is not None:
        return _now_override()
    return datetime.now(timezone.utc)


def today(tz: str) -> date:
    return now().astimezone(ZoneInfo(tz)).date()
