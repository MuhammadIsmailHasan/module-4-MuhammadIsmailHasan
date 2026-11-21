# Backend Guidelines

Coding standards for the Flask API.

---

**Rule:** Flask routes contain no business logic or direct SQLAlchemy queries —
only request parsing, calling the service layer, and returning the response.

**Rationale:** Keeps routes thin and the service layer unit-testable without
spinning up the HTTP layer.

**Example:**
```python
# Bad
@bp.route("/cards/<id>", methods=["PATCH"])
def update(id):
    card = Card.query.get(id)
    card.title = request.json["title"]
    db.session.commit()
    return jsonify({"data": card.to_dict()})

# Good
@bp.route("/cards/<id>", methods=["PATCH"])
def update(id):
    data = CardUpdateSchema().load(request.json)
    return jsonify({"data": card_service.update_card(id, data)})
```

---

**Rule:** `service.py` never issues a raw query — it calls `repository.py`,
which is the only file in a domain allowed to touch `Model.query` / the
session directly.

**Rationale:** A service that only calls repository functions is testable with
a fake repository (no real DB in unit tests), and every query for a domain
lives in one findable file.

**Example:**
```python
# repository.py
def get_by_id(card_id):
    return Card.query.filter_by(id=card_id, deleted_at=None).first_or_404()

# service.py
def move_card(card_id, to_column_id, new_order, actor_id):
    card = card_repository.get_by_id(card_id)   # not Card.query.get(card_id)
    ...
```

---

**Rule:** Every success response is `{"status": true, "message": ..., "data": ...}`;
every error is `{"status": false, "message": ..., "error": {"code": ..., "details"?: ...}}`
with the matching HTTP status (`429` included, with a `Retry-After` header and
`details.retry_after`) — produced by one shared helper, not re-typed per route.
`details` appears only for `VALIDATION_ERROR`, a registration `CONFLICT`, and
`RATE_LIMITED`. The change-password route is limited too (scope `change_password`, keyed by user id).

**Rationale:** A single helper means every endpoint's envelope is identical by
construction, not by each author remembering the convention.

**Example:**
```python
def ok(payload, message="OK", status=200):
    return jsonify({"status": True, "message": message, "data": payload}), status

def fail(code, message, status, details=None):
    error = {"code": code, **({"details": details} if details else {})}
    return jsonify({"status": False, "message": message, "error": error}), status

try:
    data = CommentCreateSchema().load(request.json)
except ValidationError as e:
    return fail("VALIDATION_ERROR", "Validation failed", 400, e.messages)
```

---

**Rule:** Authorization is checked in the service layer (or a route
decorator), never only assumed from the frontend hiding a button.

**Rationale:** A client can always call the API directly; a `403` must come
back server-side regardless of what the UI shows.

**Example:**
```python
def delete_card(user, card_id):
    require_role(user, "supervisor", "manager")
    ...
```

---

**Rule:** CORS is set up once in the app factory from an `ALLOWED_ORIGINS` env
var — never a wildcard, never configured ad hoc per blueprint.

**Rationale:** One place to see and change exactly which frontends may call
the API; a wildcard origin on an app with board/card data is a real gap, not
a lint nag.

**Example:**
```python
from flask_cors import CORS
CORS(app, origins=os.environ["ALLOWED_ORIGINS"].split(","))
```

---

**Rule:** `Card.order` / `Subtask.order` is a `db.Column(db.Float)`.
Reordering sets the moved item's order to the midpoint of its new neighbors —
never renumber every sibling.

**Rationale:** O(1) reposition on drag-and-drop instead of O(n) renumbering on
every move.

**Example:**
```python
new_order = (prev.order + next.order) / 2 if prev and next_ \
    else (prev.order + 1 if prev else next_.order - 1 if next_ else 1.0)
```

---

**Rule:** Deleting a `Board` or `Card` sets `deleted_at`; it never issues a
hard `DELETE`. Archiving sets `archived_at` and is independent of deletion.

**Rationale:** Preserves activity-log history and makes archiving reversible.

**Example:**
```python
def soft_delete_card(card):
    card.deleted_at = datetime.utcnow()
    db.session.commit()
```

---

**Rule:** Every state-changing service function writes one `ActivityLog` row
in the same transaction as the change it describes.

**Rationale:** The activity log must never be reconstructable-but-missing —
it has to be written atomically with the action it logs.

**Example:**
```python
def move_card(card_id, to_column_id, new_order, actor_id):
    card = card_repository.get_by_id(card_id)
    from_column_id = card.column_id
    card.column_id, card.order = to_column_id, new_order
    db.session.add(ActivityLog(actor_id=actor_id, action="card.moved",
                                target_type="card", target_id=card.id,
                                metadata={"from": from_column_id, "to": to_column_id}))
    db.session.commit()
    return card
```

---

**Rule:** Creating a comment reply checks that its target isn't itself a
reply before insert, and increments the parent's `reply_count` in the same
transaction. There is no like endpoint or like table anywhere in this domain.

**Rationale:** The 2-level depth cap has to hold even against a direct API
call, not just a hidden UI button; `reply_count` is what "Popular" sorts by,
so it has to be updated atomically with the insert that changes it.

**Example:**
```python
def add_reply(parent_id, author_id, content):
    parent = comment_repository.get_by_id(parent_id)
    if parent.parent_id is not None:
        raise ValidationError("cannot reply to a reply")
    reply = comment_repository.create(parent_id=parent_id, author_id=author_id, content=content)
    parent.reply_count += 1
    db.session.commit()
    return reply

def list_for_card(card_id, sort="latest"):
    order = Comment.reply_count.desc() if sort == "popular" else Comment.created_at.desc()
    return comment_repository.list_top_level(card_id).order_by(Comment.is_priority.desc(), order, Comment.created_at.desc())
```

---

**Rule:** Category mutations (`create`/`update`/`delete`) require
supervisor/manager/admin; listing a board's categories requires only board
access, the same access check (owner, board member, Manager, Admin; V12: no
public boards) used for its columns and cards. A `BoardMember` row is never
created for a Manager or an Admin, `progress` is computed (never stored or
posted), and a comment may be deleted only by its author.

**Rationale:** Categories feed the filter row everyone sees, but only the
roles that manage a board's structure should be able to change what those
filters are.

**Example:**
```python
@bp.route("/boards/<board_id>/categories", methods=["POST"])
def create_category(board_id):
    require_role(current_user, "supervisor", "manager", "admin")
    data = CategoryCreateSchema().load(request.json)
    return jsonify({"data": category_service.create(board_id, data)}), 201

@bp.route("/boards/<board_id>/categories", methods=["GET"])
def list_categories(board_id):
    require_board_access(current_user, board_id)  # no role restriction beyond this
    return jsonify({"data": category_service.list_for_board(board_id)})
```
---
**Rule:** An uploaded file is accepted by its content, not by its name: read
the leading bytes, allow a short list of types, store it under a generated
name through the one file store, and delete the replaced file only after the
database change commits.
**Rationale:** A file name and a `Content-Type` header come from the client;
a generated name also closes path tricks such as `../`.
**Example:**
```python
kind = detect_image_type(data[:12])          # "png" | "jpg" | "webp" | None
if kind is None or not 0 < len(data) <= MAX_AVATAR_BYTES:
    raise ValidationError("Invalid image", details={"file": ["Use a PNG, JPEG, or WebP image up to 2 MB."]})
name = f"{uuid4().hex}.{kind}"               # never the original file name
```

---
**Rule:** A user's `email` leaves the Backend in only three Board-scoped responses
(V12 round 2): the candidate search, `GET /boards/{id}/members?include=email`, and
`GET /boards/{id}/join-requests`, each after a role check for staff. The join
request's create and decision responses, notifications, and activity metadata
carry no email, and the pending list reads it through a join, never from a copy.
**Rationale:** A short, named list of places is the only way to review email
exposure.
**Example:** `JoinRequestUserSchema` has `email`; `JoinRequestSchema` returned by
`POST /invite/{token}/requests` has no `user` field at all.
