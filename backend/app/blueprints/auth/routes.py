from flask_smorest import Blueprint

from app.blueprints.auth import service
from app.blueprints.auth.schema import AuthSchema, AvailabilityQuerySchema, AvailabilitySchema, LoginSchema, RegisterSchema
from app.common.docs import endpoint
from app.common.envelope import NullEnvelopeSchema, envelope
from app.common.responses import ok

bp = Blueprint("auth", __name__, description="Register, log in and log out")


@bp.route("/auth/register", methods=["POST"])
@endpoint(bp, "Register an account", "Creates a member account and returns a Token.", auth="none", errors=(400, 409))
@bp.arguments(RegisterSchema)
@bp.response(201, envelope(AuthSchema))
def register(data):
    return ok(service.register(data), "User registered", 201)


@bp.route("/auth/login", methods=["POST"])
@endpoint(bp, "Log in", "The identifier is a username or an email, matched case-insensitively. One generic 401 for any mismatch.", auth="none", errors=(400, 401))
@bp.arguments(LoginSchema)
@bp.response(200, envelope(AuthSchema))
def login(data):
    return ok(service.login(data), "Logged in")


@bp.route("/auth/availability", methods=["GET"])
@endpoint(bp, "Check username and email availability", "Reports whether each supplied value is free. No Token needed.", auth="none", errors=(400,))
@bp.arguments(AvailabilityQuerySchema, location="query")
@bp.response(200, envelope(AvailabilitySchema))
def availability(args):
    return ok(service.availability(args.get("username"), args.get("email")), "OK")


@bp.route("/auth/logout", methods=["POST"])
@endpoint(bp, "Log out", "Revokes nothing; the client discards the Token, which stays valid until expiry.", auth="none", errors=())
@bp.response(200, NullEnvelopeSchema)
def logout():
    return ok(None, "Logged out")
