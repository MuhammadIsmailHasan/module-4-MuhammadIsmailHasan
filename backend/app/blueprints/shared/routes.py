from flask import request
from flask_smorest import Blueprint

from app.blueprints.cards.schema import AttachmentUrlSchema
from app.blueprints.categories.schema import CategorySchema
from app.blueprints.shared import service
from app.blueprints.shared.schema import SharedBoardSchema, SharedCardSchema, SharedCardsQuerySchema
from app.common.auth import optional_actor
from app.common.docs import endpoint
from app.common.envelope import envelope
from app.common.responses import ok

bp = Blueprint("shared", __name__, description="Read-only board view through a share link. GET only, no Token needed.")
_DOC = dict(auth="none", errors=(404,))


@bp.after_request
def _no_store(response):
    response.headers["Cache-Control"] = "private, no-store"
    return response


@bp.route("/shared/<token>", methods=["GET"])
@endpoint(bp, "Shared board", "Board name, description and columns. An unusable Bearer Token is ignored.", **_DOC)
@bp.response(200, envelope(SharedBoardSchema))
def board(token):
    return ok(service.get_board(token, optional_actor()))


@bp.route("/shared/<token>/cards", methods=["GET"])
@endpoint(bp, "Shared cards", "Same search and filters as the board card list; no comments or activity.", auth="none", errors=(400, 404))
@bp.arguments(SharedCardsQuerySchema, location="query")
@bp.response(200, envelope(SharedCardSchema, many=True))
def cards(args, token):
    return ok(service.list_cards(token, request.args))


@bp.route("/shared/<token>/categories", methods=["GET"])
@endpoint(bp, "Shared categories", **_DOC)
@bp.response(200, envelope(CategorySchema, many=True))
def categories(token):
    return ok(service.list_categories(token))


@bp.route("/shared/<token>/cards/<card_id>", methods=["GET"])
@endpoint(bp, "Shared card", "404 when the card is not on the shared board or is deleted.", **_DOC)
@bp.response(200, envelope(SharedCardSchema))
def card(token, card_id):
    return ok(service.get_card(token, card_id))


@bp.route("/shared/<token>/attachments/<attachment_id>/url", methods=["GET"])
@endpoint(bp, "Fresh signed file URL for a shared attachment", "Scoped to the Share_Token; stops working when the link is disabled or replaced.", **_DOC)
@bp.response(200, envelope(AttachmentUrlSchema))
def attachment_url(token, attachment_id):
    return ok(service.attachment_url(token, attachment_id))
