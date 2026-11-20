from flask import request
from flask_smorest import Blueprint

from app.blueprints.auth import service
from app.blueprints.auth.schema import (
    AuthSchema,
    AvailabilityQuerySchema,
    AvailabilitySchema,
    ChangePasswordSchema,
    LoginSchema,
    RegisterSchema,
    UpdateMeSchema,
    UserSchema,
)
from app.common.auth import current_actor, require_role
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
@endpoint(bp, "Log in", "The identifier is a username or an email, matched case-insensitively. One generic 401 for any mismatch.", auth="none", errors=(400, 401, 429))
@bp.arguments(LoginSchema)
@bp.response(200, envelope(AuthSchema))
def login(data):
    return ok(service.login(data, request.remote_addr), "Logged in")


@bp.route("/auth/availability", methods=["GET"])
@endpoint(bp, "Check username and email availability", "Reports whether each supplied value is free. No Token needed.", auth="none", errors=(400, 429))
@bp.arguments(AvailabilityQuerySchema, location="query")
@bp.response(200, envelope(AvailabilitySchema))
def availability(args):
    return ok(service.availability(args.get("username"), args.get("email"), request.remote_addr), "OK")


@bp.route("/auth/logout", methods=["POST"])
@endpoint(bp, "Log out", "Revokes nothing; the client discards the Token, which stays valid until expiry.", auth="none", errors=())
@bp.response(200, NullEnvelopeSchema)
def logout():
    return ok(None, "Logged out")


_ANY_ROLE = ("member", "supervisor", "manager", "admin")


@bp.route("/auth/me", methods=["GET"])
@endpoint(bp, "Get the signed-in user", "Returns the user shape of register and login.", errors=(401,))
@require_role(*_ANY_ROLE)
@bp.response(200, envelope(UserSchema))
def me():
    return ok(service.get_me(current_actor()), "OK")


@bp.route("/auth/me", methods=["PATCH"])
@endpoint(bp, "Update the profile", "Only `full_name`; any other field is a 400.", errors=(400, 401))
@require_role(*_ANY_ROLE)
@bp.arguments(UpdateMeSchema)
@bp.response(200, envelope(UserSchema))
def update_me(data):
    return ok(service.update_me(current_actor(), data), "Profile updated")


@bp.route("/auth/change-password", methods=["POST"])
@endpoint(bp, "Change the password", "A wrong current password is a 400 (never 401) and is counted; the issued Token stays valid.", errors=(400, 401, 429))
@require_role(*_ANY_ROLE)
@bp.arguments(ChangePasswordSchema)
@bp.response(200, NullEnvelopeSchema)
def change_password(data):
    service.change_password(current_actor(), data)
    return ok(None, "Password changed")
