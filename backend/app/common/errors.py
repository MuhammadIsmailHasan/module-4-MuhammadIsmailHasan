class AppError(Exception):
    status = 500
    code = "INTERNAL_ERROR"

    def __init__(self, message="Internal server error"):
        super().__init__(message)
        self.message = message


class ValidationError(AppError):
    status = 400
    code = "VALIDATION_ERROR"


class Unauthorized(AppError):
    status = 401
    code = "UNAUTHORIZED"


class Forbidden(AppError):
    status = 403
    code = "FORBIDDEN"


class NotFound(AppError):
    status = 404
    code = "NOT_FOUND"


class Conflict(AppError):
    status = 409
    code = "CONFLICT"


def error_body(status, code, message):
    """Error envelope: { status, message, error: { code, message } }."""
    return {"status": status, "message": message, "error": {"code": code, "message": message}}
