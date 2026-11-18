from flask_smorest import Blueprint

from app.blueprints.auth import service
from app.blueprints.auth.schema import AuthSchema, LoginSchema, RegisterSchema
from app.common.docs import endpoint
from app.common.envelope import NullEnvelopeSchema, envelope
from app.common.responses import ok

bp = Blueprint("auth", __name__, description="Register, log in and log out")


@bp.route("/auth/register", methods=["POST"])
@endpoint(bp, "Register an account", "Creates a member account and returns a Token.", auth="none", errors=(400, 409))
@bp.arguments(RegisterSchema)
@bp.response(201, envelope(AuthSchema))
def register(data):
    return ok(service.register(data), "Registered", 201)


@bp.route("/auth/login", methods=["POST"])
@endpoint(bp, "Log in", "login_identifier is matched case-insensitively.", auth="none", errors=(400, 401))
@bp.arguments(LoginSchema)
@bp.response(200, envelope(AuthSchema))
def login(data):
    return ok(service.login(data), "Logged in")


@bp.route("/auth/logout", methods=["POST"])
@endpoint(bp, "Log out", "Revokes nothing; the client discards the Token, which stays valid until expiry.", auth="none", errors=())
@bp.response(200, NullEnvelopeSchema)
def logout():
    return ok(None, "Logged out")
