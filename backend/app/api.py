"""The single flask-smorest Api: envelope error rendering, OpenAPI config gated by APP_ENV."""
import json
import logging
from http import HTTPStatus
from pathlib import Path

from flask import jsonify
from flask_smorest import Api
from werkzeug.exceptions import HTTPException

from app.common.envelope import ErrorEnvelopeSchema
from app.common.errors import AppError, error_body
from app.extensions import db

log = logging.getLogger(__name__)

DOCS_ENVS = ("development", "testing")
_CODES = {
    400: "VALIDATION_ERROR",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
}


def render_error(status, code, message):
    return jsonify(error_body(status, code, message)), status


def openapi_config(app_env):
    config = {"API_TITLE": "Kanban Task Management API", "API_VERSION": "v1", "OPENAPI_VERSION": "3.0.3"}
    if app_env in DOCS_ENVS:
        config.update(
            OPENAPI_URL_PREFIX="/api",
            OPENAPI_JSON_PATH="openapi.json",
            OPENAPI_SWAGGER_UI_PATH="docs",
            OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
        )
    return config


def _first_message(messages):
    """Flatten webargs/marshmallow messages to 'field: text' for the first problem."""
    if isinstance(messages, dict):
        for key, value in messages.items():
            inner = _first_message(value)
            if inner is None:
                continue
            field, text = inner
            return (field or (key if key not in ("json", "query", "form", "files") else None), text)
        return None
    if isinstance(messages, (list, tuple)):
        for item in messages:
            inner = _first_message(item)
            if inner:
                return inner
        return None
    return (None, str(messages))


class EnvelopeApi(Api):
    ERROR_SCHEMA = ErrorEnvelopeSchema

    def _register_error_handlers(self):
        app = self._app
        app.register_error_handler(AppError, self.handle_app_error)
        app.register_error_handler(HTTPException, self.handle_http_exception)
        app.register_error_handler(Exception, self.handle_unexpected)

    def handle_app_error(self, err):
        db.session.rollback()
        return render_error(err.status, err.code, err.message)

    def handle_http_exception(self, error):
        status = error.code or 500
        data = getattr(error, "data", None) or {}
        if status == 422:  # smorest/webargs validation failure -> 400, never 422
            found = _first_message(data.get("messages") or data.get("errors") or data.get("message"))
            field, text = found if found else (None, "Invalid request")
            if field and not text.lower().startswith(field.lower()):
                text = f"{field}: {text}"
            return render_error(400, "VALIDATION_ERROR", text)
        message = data.get("message") or HTTPStatus(status).phrase
        return render_error(status, _CODES.get(status, "ERROR"), message)

    def handle_unexpected(self, err):
        db.session.rollback()
        log.exception("Unhandled exception")
        return render_error(500, "INTERNAL_ERROR", "Internal server error")


def init_api(app):
    api = EnvelopeApi(app)
    app.extensions["api"] = api
    api.spec.components.security_scheme(
        "bearerAuth", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    )

    @app.cli.command("export-openapi")
    def export_openapi():
        """Write the generated OpenAPI document to backend/openapi.json."""
        path = Path(app.root_path).parent / "openapi.json"
        path.write_text(json.dumps(api.spec.to_dict(), indent=2) + "\n")
        print(f"Wrote {path}")

    return api
