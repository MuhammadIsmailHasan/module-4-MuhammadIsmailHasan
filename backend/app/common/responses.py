from http import HTTPStatus


def ok(data=None, message=None, status=200):
    """Success envelope: { status, message, data }. Default message is the HTTP reason phrase."""
    return {"status": status, "message": message or HTTPStatus(status).phrase, "data": data}
