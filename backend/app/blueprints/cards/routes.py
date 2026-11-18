from flask import Blueprint, request, send_file

from app.blueprints.activity import repository as activity
from app.blueprints.cards import service
from app.blueprints.cards.schema import serialize_attachment, serialize_card, serialize_subtask
from app.common.auth import current_actor, require_role
from app.common.errors import Forbidden
from app.common.http import json_body
from app.common.responses import ok

bp = Blueprint("cards", __name__)
USERS = ("member", "supervisor", "manager", "admin")


@bp.post("/columns/<column_id>/cards")
@require_role(*USERS)
def create_card(column_id):
    actor = current_actor()
    return ok(service.present(service.create_card(actor, column_id, json_body()), actor), 201)


@bp.get("/cards/<card_id>")
def get_card(card_id):
    actor = current_actor()
    return ok(service.present(service.get_card(actor, card_id), actor))


@bp.patch("/cards/<card_id>")
@require_role(*USERS)
def update_card(card_id):
    actor = current_actor()
    return ok(service.present(service.update_card(actor, card_id, json_body()), actor))


@bp.delete("/cards/<card_id>")
@require_role(*USERS)
def delete_card(card_id):
    service.delete_card(current_actor(), card_id)
    return ok(None)


@bp.post("/cards/<card_id>/archive")
@require_role(*USERS)
def archive(card_id):
    actor = current_actor()
    return ok(service.present(service.set_archived(actor, card_id, True), actor))


@bp.post("/cards/<card_id>/unarchive")
@require_role(*USERS)
def unarchive(card_id):
    actor = current_actor()
    return ok(service.present(service.set_archived(actor, card_id, False), actor))


@bp.patch("/cards/<card_id>/move")
@require_role(*USERS)
def move(card_id):
    actor = current_actor()
    return ok(service.present(service.move_card(actor, card_id, json_body()), actor))


@bp.get("/cards/<card_id>/activity")
def card_activity(card_id):
    actor = current_actor()
    card = service.get_card(actor, card_id)
    if actor is None:
        raise Forbidden("Activity is not available to guests")
    return ok([activity.serialize(r) for r in activity.for_card(card.id)])


@bp.get("/boards/<board_id>/cards")
def board_cards(board_id):
    return ok(service.list_board_cards(current_actor(), board_id, request.args))


@bp.post("/cards/<card_id>/subtasks")
@require_role(*USERS)
def add_subtask(card_id):
    return ok(serialize_subtask(service.add_subtask(current_actor(), card_id, json_body())), 201)


@bp.patch("/subtasks/<subtask_id>")
@require_role(*USERS)
def update_subtask(subtask_id):
    return ok(serialize_subtask(service.update_subtask(current_actor(), subtask_id, json_body())))


@bp.delete("/subtasks/<subtask_id>")
@require_role(*USERS)
def delete_subtask(subtask_id):
    service.delete_subtask(current_actor(), subtask_id)
    return ok(None)


@bp.post("/cards/<card_id>/attachments")
@require_role(*USERS)
def add_attachment(card_id):
    upload = request.files.get("file")
    data = request.form.to_dict() if upload is not None else json_body()
    return ok(serialize_attachment(service.add_attachment(current_actor(), card_id, data, upload)), 201)


@bp.delete("/attachments/<attachment_id>")
@require_role(*USERS)
def delete_attachment(attachment_id):
    service.delete_attachment(current_actor(), attachment_id)
    return ok(None)


@bp.get("/attachments/<attachment_id>/url")
def attachment_url(attachment_id):
    return ok(service.attachment_url(current_actor(), attachment_id))


@bp.get("/attachments/<attachment_id>/file")
def attachment_file(attachment_id):
    path, att = service.attachment_file_path(attachment_id, request.args.get("exp"), request.args.get("sig"))
    return send_file(path, mimetype=att.mime_type, as_attachment=True, download_name=att.name)
