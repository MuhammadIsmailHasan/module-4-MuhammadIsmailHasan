import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

log = logging.getLogger(__name__)


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


def error_response(status, code, message):
    return jsonify({"error": {"code": code, "message": message}}), status


_HTTP_CODES = {
    400: "VALIDATION_ERROR",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
}


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def _app_error(err):
        from app.extensions import db

        db.session.rollback()
        return error_response(err.status, err.code, err.message)

    @app.errorhandler(HTTPException)
    def _http_error(err):
        code = _HTTP_CODES.get(err.code, "ERROR")
        return error_response(err.code or 500, code, err.description or err.name)

    @app.errorhandler(Exception)
    def _unhandled(err):
        from app.extensions import db

        db.session.rollback()
        log.exception("Unhandled exception")
        return error_response(500, "INTERNAL_ERROR", "Internal server error")
