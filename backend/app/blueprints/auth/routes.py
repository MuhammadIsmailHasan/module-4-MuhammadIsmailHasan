from flask import Blueprint

from app.blueprints.auth import service
from app.common.http import json_body
from app.common.responses import ok

bp = Blueprint("auth", __name__)


@bp.post("/auth/register")
def register():
    return ok(service.register(json_body()), 201)


@bp.post("/auth/login")
def login():
    return ok(service.login(json_body()))


@bp.post("/auth/logout")
def logout():
    # Stateless Token, no revocation list.
    return ok(None)
