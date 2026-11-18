import os
from datetime import timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import Flask
from flask_cors import CORS

from app.common.auth import register_jwt_callbacks
from app.api import init_api, openapi_config
from app.extensions import db, jwt, migrate

REQUIRED_ENV = ("ALLOWED_ORIGINS", "JWT_SECRET", "FILE_URL_SECRET", "APP_TIMEZONE")


def _load_config(overrides):
    env = os.environ
    missing = [k for k in REQUIRED_ENV if not env.get(k, "").strip()]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    origins = [o.strip() for o in env["ALLOWED_ORIGINS"].split(",") if o.strip()]
    if not origins or "*" in origins:
        raise RuntimeError("ALLOWED_ORIGINS must be an explicit origin list and must not contain '*'")

    tz = env["APP_TIMEZONE"].strip()
    try:
        ZoneInfo(tz)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise RuntimeError(f"APP_TIMEZONE is not a valid IANA name: {tz}") from exc

    config = {
        "SQLALCHEMY_DATABASE_URI": env.get("DATABASE_URL") or None,
        "JWT_SECRET_KEY": env["JWT_SECRET"],
        "JWT_ACCESS_TOKEN_EXPIRES": timedelta(hours=24),
        "FILE_URL_SECRET": env["FILE_URL_SECRET"],
        "APP_TIMEZONE": tz,
        "UPLOAD_DIR": env.get("UPLOAD_DIR") or "uploads",
        "ALLOWED_ORIGINS": origins,
        "APP_ENV": (env.get("APP_ENV") or "production").strip().lower(),
    }
    config.update(overrides)
    config.update(openapi_config(config["APP_ENV"]))
    return config


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.update(_load_config(config_overrides or {}))
    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        raise RuntimeError("DATABASE_URL is required")

    # One app-wide CORS policy; no cookies are used, so credentials stay off.
    CORS(app, origins=app.config["ALLOWED_ORIGINS"], supports_credentials=False)

    db.init_app(app)
    from app import models  # noqa: F401  (register models for migrations)

    migrate.init_app(app, db)
    jwt.init_app(app)
    register_jwt_callbacks(jwt)
    api = init_api(app)

    from app.blueprints import register_blueprints

    register_blueprints(api)

    from app.seed import register_cli

    register_cli(app)

    from app.jobs.deadlines import register_cli as register_job_cli

    register_job_cli(app)
    return app
