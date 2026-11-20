from flask_smorest import Blueprint

from app.blueprints.categories import service
from app.blueprints.categories.schema import CategorySchema, CreateCategorySchema, UpdateCategorySchema
from app.common.auth import current_actor, require_role
from app.common.docs import endpoint
from app.common.envelope import NullEnvelopeSchema, envelope
from app.common.responses import ok

bp = Blueprint("categories", __name__, description="Board-scoped categories")
USERS = ("member", "supervisor", "manager", "admin")


@bp.route("/boards/<board_id>/categories", methods=["GET"])
@endpoint(bp, "List a board's categories", "Requires board access.")
@require_role(*USERS)
@bp.response(200, envelope(CategorySchema, many=True))
def list_categories(board_id):
    return ok([service.serialize(c) for c in service.list_categories(current_actor(), board_id)])


@bp.route("/boards/<board_id>/categories", methods=["POST"])
@endpoint(bp, "Create a category", "Staff access. 409 on a case-insensitive duplicate name.", errors=(400, 401, 403, 404, 409))
@require_role(*USERS)
@bp.arguments(CreateCategorySchema)
@bp.response(201, envelope(CategorySchema))
def create(data, board_id):
    return ok(service.serialize(service.create(current_actor(), board_id, data)), "Category created", 201)


@bp.route("/categories/<category_id>", methods=["PATCH"])
@endpoint(bp, "Rename or recolor a category", "Staff access. 409 on a case-insensitive duplicate name.", errors=(400, 401, 403, 404, 409))
@require_role(*USERS)
@bp.arguments(UpdateCategorySchema)
@bp.response(200, envelope(CategorySchema))
def update(data, category_id):
    return ok(service.serialize(service.update(current_actor(), category_id, data)), "Category updated")


@bp.route("/categories/<category_id>", methods=["DELETE"])
@endpoint(bp, "Delete a category", "Staff access. Cards in it get category_id = null.", errors=(401, 403, 404))
@require_role(*USERS)
@bp.response(200, NullEnvelopeSchema)
def delete(category_id):
    service.delete(current_actor(), category_id)
    return ok(None, "Category deleted")
