from flask import request, send_file
from flask_smorest import Blueprint

from app.blueprints.activity import repository as activity
from app.blueprints.activity.schema import ActivitySchema
from app.blueprints.cards import service
from app.blueprints.cards.dto import serialize_attachment, serialize_card, serialize_subtask
from app.blueprints.cards.schema import (
    AttachmentSchema,
    AttachmentUrlSchema,
    BoardCardsQuerySchema,
    CardSchema,
    CreateCardSchema,
    CreateSubtaskSchema,
    MoveCardSchema,
    SubtaskSchema,
    UpdateCardSchema,
    UpdateSubtaskSchema,
)
from app.common.auth import current_actor, require_role
from app.common.docs import endpoint
from app.common.envelope import NullEnvelopeSchema, envelope
from app.common.errors import Forbidden
from app.common.http import json_body
from app.common.responses import ok

bp = Blueprint("cards", __name__, description="Cards, move, subtasks, attachments, activity and search")
USERS = ("member", "supervisor", "manager", "admin")

_ATTACHMENT_BODY = {
    "required": True,
    "content": {
        "application/json": {
            "schema": {
                "type": "object",
                "required": ["url"],
                "properties": {"name": {"type": "string"}, "url": {"type": "string", "format": "uri"}},
            }
        },
        "multipart/form-data": {
            "schema": {
                "type": "object",
                "required": ["file"],
                "properties": {"file": {"type": "string", "format": "binary", "description": "PDF, Word or RAR"}},
            }
        },
    },
}


@bp.route("/columns/<column_id>/cards", methods=["POST"])
@endpoint(bp, "Create a card", "Staff access on the board; Members get 403. order = max + 1 in the column.", errors=(400, 401, 403, 404))
@require_role(*USERS)
@bp.arguments(CreateCardSchema)
@bp.response(201, envelope(CardSchema))
def create_card(data, column_id):
    actor = current_actor()
    return ok(service.present(service.create_card(actor, column_id, data), actor), "Card created", 201)


@bp.route("/cards/<card_id>", methods=["GET"])
@endpoint(bp, "Get a card", "Guests may read public boards; comments and activity are omitted for Guests.", auth="optional")
@bp.response(200, envelope(CardSchema))
def get_card(card_id):
    actor = current_actor()
    return ok(service.present(service.get_card(actor, card_id), actor), "Card retrieved")


@bp.route("/cards/<card_id>", methods=["PATCH"])
@endpoint(bp, "Update a card", "Member only when assigned (and cannot change the assignee); staff need board staff access.", errors=(400, 401, 403, 404))
@require_role(*USERS)
@bp.arguments(UpdateCardSchema)
@bp.response(200, envelope(CardSchema))
def update_card(data, card_id):
    actor = current_actor()
    return ok(service.present(service.update_card(actor, card_id, data), actor), "Card updated")


@bp.route("/cards/<card_id>", methods=["DELETE"])
@endpoint(bp, "Soft-delete a card", "Staff access. Sets deleted_at; children are hidden, never removed.", errors=(401, 403, 404))
@require_role(*USERS)
@bp.response(200, NullEnvelopeSchema)
def delete_card(card_id):
    service.delete_card(current_actor(), card_id)
    return ok(None, "Card deleted")


@bp.route("/cards/<card_id>/archive", methods=["POST"])
@endpoint(bp, "Archive a card", "Staff access.", errors=(401, 403, 404))
@require_role(*USERS)
@bp.response(200, envelope(CardSchema))
def archive(card_id):
    actor = current_actor()
    return ok(service.present(service.set_archived(actor, card_id, True), actor), "Card archived")


@bp.route("/cards/<card_id>/unarchive", methods=["POST"])
@endpoint(bp, "Unarchive a card", "Staff access.", errors=(401, 403, 404))
@require_role(*USERS)
@bp.response(200, envelope(CardSchema))
def unarchive(card_id):
    actor = current_actor()
    return ok(service.present(service.set_archived(actor, card_id, False), actor), "Card unarchived")


@bp.route("/cards/<card_id>/move", methods=["PATCH"])
@endpoint(bp, "Move or reorder a card", "Member only when assigned; staff need board staff access. The server computes order from the prev/next neighbours and ignores any client order. 400 when the column is on another board.", errors=(400, 401, 403, 404))
@require_role(*USERS)
@bp.arguments(MoveCardSchema)
@bp.response(200, envelope(CardSchema))
def move(data, card_id):
    actor = current_actor()
    return ok(service.present(service.move_card(actor, card_id, data), actor), "Card moved")


@bp.route("/cards/<card_id>/activity", methods=["GET"])
@endpoint(bp, "Card activity", "Requires board access; Guests get 403.", auth="optional")
@bp.response(200, envelope(ActivitySchema, many=True))
def card_activity(card_id):
    actor = current_actor()
    card = service.get_card(actor, card_id)
    if actor is None:
        raise Forbidden("Activity is not available to guests")
    return ok([activity.serialize(r) for r in activity.for_card(card.id)], "Activity retrieved")


@bp.route("/boards/<board_id>/cards", methods=["GET"])
@endpoint(bp, "Search and filter a board's cards", "Filters combine with AND; an unsupported filter[...] key returns 400. Soft-deleted cards are excluded.", auth="optional")
@bp.arguments(BoardCardsQuerySchema, location="query")
@bp.response(200, envelope(CardSchema, many=True))
def board_cards(args, board_id):
    return ok(service.list_board_cards(current_actor(), board_id, request.args), "Cards retrieved")


@bp.route("/cards/<card_id>/subtasks", methods=["POST"])
@endpoint(bp, "Add a subtask", "Same edit rights as the card.", errors=(400, 401, 403, 404))
@require_role(*USERS)
@bp.arguments(CreateSubtaskSchema)
@bp.response(201, envelope(SubtaskSchema))
def add_subtask(data, card_id):
    return ok(serialize_subtask(service.add_subtask(current_actor(), card_id, data)), "Subtask created", 201)


@bp.route("/subtasks/<subtask_id>", methods=["PATCH"])
@endpoint(bp, "Edit, toggle or reorder a subtask", "Send title, is_done, order, or prev/next sibling ids.", errors=(400, 401, 403, 404))
@require_role(*USERS)
@bp.arguments(UpdateSubtaskSchema)
@bp.response(200, envelope(SubtaskSchema))
def update_subtask(data, subtask_id):
    return ok(serialize_subtask(service.update_subtask(current_actor(), subtask_id, data)), "Subtask updated")


@bp.route("/subtasks/<subtask_id>", methods=["DELETE"])
@endpoint(bp, "Delete a subtask", errors=(401, 403, 404))
@require_role(*USERS)
@bp.response(200, NullEnvelopeSchema)
def delete_subtask(subtask_id):
    service.delete_subtask(current_actor(), subtask_id)
    return ok(None, "Subtask deleted")


@bp.route("/cards/<card_id>/attachments", methods=["POST"])
@endpoint(bp, "Add an attachment", "JSON link or multipart upload (PDF, Word, RAR only). Uploads are stored privately and served through signed URLs.", errors=(400, 401, 403, 404), requestBody=_ATTACHMENT_BODY)
@require_role(*USERS)
@bp.response(201, envelope(AttachmentSchema))
def add_attachment(card_id):
    upload = request.files.get("file")
    data = request.form.to_dict() if upload is not None else json_body()
    att = service.add_attachment(current_actor(), card_id, data, upload)
    return ok(serialize_attachment(att), "Attachment created", 201)


@bp.route("/attachments/<attachment_id>", methods=["DELETE"])
@endpoint(bp, "Delete an attachment", errors=(401, 403, 404))
@require_role(*USERS)
@bp.response(200, NullEnvelopeSchema)
def delete_attachment(attachment_id):
    service.delete_attachment(current_actor(), attachment_id)
    return ok(None, "Attachment deleted")


@bp.route("/attachments/<attachment_id>/url", methods=["GET"])
@endpoint(bp, "Issue a fresh signed file URL", "Re-checks board access; open to Guests on public boards. The URL is valid 15 minutes.", auth="optional")
@bp.response(200, envelope(AttachmentUrlSchema))
def attachment_url(attachment_id):
    return ok(service.attachment_url(current_actor(), attachment_id), "File URL issued")


@bp.route("/attachments/<attachment_id>/file", methods=["GET"])
@endpoint(
    bp,
    "Download an uploaded file",
    "No Token: access is the HMAC signature (exp and sig query values). Returns raw bytes on success, the error envelope otherwise.",
    auth="none",
    errors=(403, 404),
    responses={"200": {"description": "File bytes", "content": {"application/octet-stream": {"schema": {"type": "string", "format": "binary"}}}}},
)
def attachment_file(attachment_id):
    path, att = service.attachment_file_path(attachment_id, request.args.get("exp"), request.args.get("sig"))
    return send_file(path, mimetype=att.mime_type, as_attachment=True, download_name=att.name)
