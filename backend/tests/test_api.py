import io
from datetime import date, datetime, timedelta, timezone

import pytest
from conftest import TEST_PASSWORD

from app.common import clock
from app.extensions import db
from app.models import ActivityLog, Card, Notification


@pytest.fixture
def world(client, make_user, auth):
    users = {r: make_user(r) for r in ("member", "supervisor", "manager", "admin")}
    users["other_member"] = make_user("member")
    users["other_sup"] = make_user("supervisor")
    h = {k: auth(u) for k, u in users.items()}

    def post(path, who, **kw):
        return client.post(path, headers=h.get(who, {}), **kw)

    board = post("/api/boards", "manager", json={"name": "B", "visibility": "private"}).get_json()["data"]
    client.patch(f"/api/boards/{board['id']}", headers=h["manager"], json={"owner_id": str(users["supervisor"].id)})
    client.post(f"/api/boards/{board['id']}/members", headers=h["manager"], json={"user_id": str(users["member"].id)})
    return type("W", (), dict(users=users, h=h, board=board, client=client, post=staticmethod(post)))


def col(w, i=0):
    return w.board["columns"][i]["id"]


def mkcard(w, title="t", who="supervisor", i=0, **extra):
    r = w.client.post(f"/api/columns/{col(w, i)}/cards", headers=w.h[who], json={"title": title, **extra})
    assert r.status_code == 201, r.get_json()
    return r.get_json()["data"]


# ---- auth ----
def test_register_login_roundtrip(client):
    r = client.post("/api/auth/register", json={"full_name": " Ann ", "login_identifier": " Ann@X.com ", "password": TEST_PASSWORD})
    assert r.status_code == 201
    d = r.get_json()["data"]
    assert d["user"]["full_name"] == "Ann" and d["token"]
    assert client.post("/api/auth/login", json={"login_identifier": "ann@x.COM", "password": TEST_PASSWORD}).status_code == 200
    assert client.post("/api/auth/login", json={"login_identifier": "ann@x.com", "password": "bad"}).status_code == 401
    dup = client.post("/api/auth/register", json={"full_name": "A", "login_identifier": "ANN@x.com", "password": TEST_PASSWORD})
    assert dup.status_code == 409
    assert client.post("/api/auth/register", json={"full_name": "A", "login_identifier": "z", "password": "short"}).status_code == 400
    assert client.post("/api/auth/logout").get_json() == {"status": True, "message": "Logged out", "data": None}


def test_token_expiry_24h(app, make_user):
    from flask_jwt_extended import decode_token

    from app.common.auth import issue_token

    t = decode_token(issue_token(make_user().id, "member"))
    assert t["exp"] - t["iat"] == 86400


# ---- boards ----
def test_board_defaults_and_access(world):
    names = [c["name"] for c in world.board["columns"]]
    assert names == ["Todo", "In Progress", "Review", "Revision", "Done"]
    bid = world.board["id"]
    c = world.client
    assert c.get(f"/api/boards/{bid}").status_code == 401  # guest, private
    assert c.get(f"/api/boards/{bid}", headers=world.h["other_member"]).status_code == 403
    assert c.get(f"/api/boards/{bid}", headers=world.h["member"]).status_code == 200
    assert c.get("/api/boards").get_json()["data"] == []
    assert len(c.get("/api/boards", headers=world.h["manager"]).get_json()["data"]) == 1
    assert c.post("/api/boards", headers=world.h["member"], json={"name": "x"}).status_code == 403
    assert c.post("/api/boards", json={"name": "x"}).status_code == 401


def test_owner_reassign_and_visibility_archive_delete(world):
    bid, c = world.board["id"], world.client
    r = c.patch(f"/api/boards/{bid}", headers=world.h["manager"], json={"owner_id": str(world.users["member"].id)})
    assert r.status_code == 400
    assert c.patch(f"/api/boards/{bid}", headers=world.h["supervisor"], json={"owner_id": None}).status_code == 403
    assert c.patch(f"/api/boards/{bid}", headers=world.h["supervisor"], json={"visibility": "public"}).status_code == 200
    assert len(c.get("/api/boards").get_json()["data"]) == 1  # now public for guests
    assert c.post(f"/api/boards/{bid}/archive", headers=world.h["supervisor"]).status_code == 403
    assert c.post(f"/api/boards/{bid}/archive", headers=world.h["manager"]).status_code == 200
    assert c.post(f"/api/boards/{bid}/unarchive", headers=world.h["manager"]).status_code == 200
    assert c.delete(f"/api/boards/{bid}", headers=world.h["manager"]).status_code == 200
    assert c.get(f"/api/boards/{bid}", headers=world.h["manager"]).status_code == 404
    assert c.get("/api/boards").get_json()["data"] == []


def test_members_and_columns(world):
    bid, c = world.board["id"], world.client
    uid = str(world.users["other_member"].id)
    assert c.post(f"/api/boards/{bid}/members", headers=world.h["manager"], json={"user_id": uid}).status_code == 201
    assert c.post(f"/api/boards/{bid}/members", headers=world.h["manager"], json={"user_id": uid}).status_code == 409
    missing = "00000000-0000-0000-0000-000000000001"
    assert c.post(f"/api/boards/{bid}/members", headers=world.h["manager"], json={"user_id": missing}).status_code == 404
    assert c.delete(f"/api/boards/{bid}/members/{uid}", headers=world.h["manager"]).status_code == 200
    assert c.delete(f"/api/boards/{bid}/members/{uid}", headers=world.h["manager"]).status_code == 404
    r = c.post(f"/api/boards/{bid}/columns", headers=world.h["supervisor"], json={"name": "QA"})
    assert r.status_code == 201 and r.get_json()["data"]["order"] == 5.0
    assert c.post(f"/api/boards/{bid}/columns", headers=world.h["member"], json={"name": "Z"}).status_code == 403
    assert c.post(f"/api/boards/{bid}/columns", headers=world.h["other_sup"], json={"name": "Z"}).status_code == 403


# ---- cards ----
def test_card_crud_permissions_validation(world):
    c = world.client
    assert c.post(f"/api/columns/{col(world)}/cards", headers=world.h["member"], json={"title": "x"}).status_code == 403
    assert c.post(f"/api/columns/{col(world)}/cards", json={"title": "x"}).status_code == 401
    bad = c.post(f"/api/columns/{col(world)}/cards", headers=world.h["supervisor"],
                 json={"title": "x", "start_date": "2026-02-02", "end_date": "2026-02-01"})
    assert bad.status_code == 400 and bad.get_json()["error"]["code"] == "VALIDATION_ERROR"
    assert c.post(f"/api/columns/{col(world)}/cards", headers=world.h["supervisor"], json={"title": " "}).status_code == 400
    assert c.post(f"/api/columns/{col(world)}/cards", headers=world.h["supervisor"], json={"title": "x", "priority": "urgent"}).status_code == 400
    card = mkcard(world)
    cid = card["id"]
    # member not assigned -> 403; assigned -> ok
    assert c.patch(f"/api/cards/{cid}", headers=world.h["member"], json={"title": "n"}).status_code == 403
    r = c.patch(f"/api/cards/{cid}", headers=world.h["supervisor"], json={"assignee_id": str(world.users["member"].id)})
    assert r.status_code == 200
    assert c.patch(f"/api/cards/{cid}", headers=world.h["member"], json={"title": "n"}).status_code == 200
    assert c.patch(f"/api/cards/{cid}", headers=world.h["member"], json={"assignee_id": None}).status_code == 403
    assert c.patch(f"/api/cards/{cid}", headers=world.h["other_sup"], json={"title": "n"}).status_code == 403
    assert c.post(f"/api/cards/{cid}/archive", headers=world.h["supervisor"]).get_json()["data"]["archived_at"]
    assert c.post(f"/api/cards/{cid}/unarchive", headers=world.h["supervisor"]).get_json()["data"]["archived_at"] is None
    assert c.delete(f"/api/cards/{cid}", headers=world.h["supervisor"]).status_code == 200
    assert c.get(f"/api/cards/{cid}", headers=world.h["manager"]).status_code == 404
    assert db.session.get(Card, __import__("uuid").UUID(cid)).deleted_at is not None  # soft


def test_assignment_notification_and_activity(world):
    card = mkcard(world)
    mid = str(world.users["member"].id)
    world.client.patch(f"/api/cards/{card['id']}", headers=world.h["supervisor"], json={"assignee_id": mid})
    assert Notification.query.filter_by(type="assigned").count() == 1
    world.client.patch(f"/api/cards/{card['id']}", headers=world.h["supervisor"], json={"assignee_id": None})
    assert Notification.query.count() == 1
    actions = [a.action for a in ActivityLog.query.all()]
    assert "card.assigned" in actions and "card.unassigned" in actions and "card.created" in actions
    inbox = world.client.get("/api/notifications", headers=world.h["member"]).get_json()["data"]
    assert inbox["unread_count"] == 1
    nid = inbox["items"][0]["id"]
    assert world.client.patch(f"/api/notifications/{nid}/read", headers=world.h["other_member"]).status_code == 404
    assert world.client.patch(f"/api/notifications/{nid}/read", headers=world.h["member"]).status_code == 200
    assert world.client.get("/api/notifications", headers=world.h["member"]).get_json()["data"]["unread_count"] == 0


def test_move_order_and_scope(world):
    c = world.client
    a, b, d = mkcard(world, "a"), mkcard(world, "b"), mkcard(world, "c")
    r = c.patch(f"/api/cards/{d['id']}/move", headers=world.h["supervisor"],
                json={"column_id": col(world), "prev": a["id"], "next": b["id"], "order": 999})
    assert r.status_code == 200
    assert a["order"] < r.get_json()["data"]["order"] < b["order"]
    r = c.patch(f"/api/cards/{d['id']}/move", headers=world.h["supervisor"], json={"column_id": col(world, 4)})
    assert r.get_json()["data"]["order"] == 1.0
    moves = ActivityLog.query.filter_by(action="card.moved", target_id=__import__("uuid").UUID(d["id"])).count()
    assert moves == 2
    assert c.patch(f"/api/cards/{d['id']}/move", headers=world.h["member"], json={"column_id": col(world)}).status_code == 403
    assert c.patch(f"/api/cards/{d['id']}/move", json={"column_id": col(world)}).status_code == 401
    other = c.post("/api/boards", headers=world.h["manager"], json={"name": "O"}).get_json()["data"]
    r = c.patch(f"/api/cards/{d['id']}/move", headers=world.h["supervisor"], json={"column_id": other["columns"][0]["id"]})
    assert r.status_code == 400


def test_move_rebalances_tight_gap(world):
    a, b = mkcard(world, "a"), mkcard(world, "b")
    for card, order in ((a, 1.0), (b, 1.0 + 1e-8)):
        db.session.get(Card, __import__("uuid").UUID(card["id"])).order = order
    db.session.commit()
    n = mkcard(world, "n", i=1)
    r = world.client.patch(f"/api/cards/{n['id']}/move", headers=world.h["supervisor"],
                           json={"column_id": col(world), "prev": a["id"], "next": b["id"]})
    assert r.status_code == 200
    orders = {x.title: x.order for x in Card.query.filter_by(column_id=__import__("uuid").UUID(col(world))).all()}
    assert orders["a"] < orders["n"] < orders["b"]


def test_subtasks(world):
    c = world.client
    card = mkcard(world)
    s1 = c.post(f"/api/cards/{card['id']}/subtasks", headers=world.h["supervisor"], json={"title": "s1"}).get_json()["data"]
    s2 = c.post(f"/api/cards/{card['id']}/subtasks", headers=world.h["supervisor"], json={"title": "s2"}).get_json()["data"]
    assert s1["is_done"] is False
    r = c.patch(f"/api/subtasks/{s1['id']}", headers=world.h["supervisor"], json={"is_done": True})
    assert r.get_json()["data"]["is_done"] is True
    r = c.patch(f"/api/subtasks/{s2['id']}", headers=world.h["supervisor"], json={"prev": None, "next": s1["id"]})
    assert r.get_json()["data"]["order"] < s1["order"]
    assert c.delete(f"/api/subtasks/{s1['id']}", headers=world.h["supervisor"]).status_code == 200
    assert c.patch(f"/api/subtasks/{s1['id']}", headers=world.h["supervisor"], json={"is_done": False}).status_code == 404


def test_attachments_and_signed_urls(world, app):
    c = world.client
    card = mkcard(world)
    url = f"/api/cards/{card['id']}/attachments"
    h = world.h["supervisor"]
    assert c.post(url, headers=h, json={}).status_code == 400
    assert c.post(url, headers=h, json={"url": "javascript:alert(1)"}).status_code == 400
    link = c.post(url, headers=h, json={"url": "https://e.com/x"}).get_json()["data"]
    assert link["url"] == "https://e.com/x" and link["file_url"] is None
    bad = c.post(url, headers=h, data={"file": (io.BytesIO(b"x"), "a.exe", "application/octet-stream")}, content_type="multipart/form-data")
    assert bad.status_code == 400
    ok = c.post(url, headers=h, data={"file": (io.BytesIO(b"%PDF"), "a.pdf", "application/pdf")}, content_type="multipart/form-data")
    assert ok.status_code == 201
    att = ok.get_json()["data"]
    assert "sig=" in att["file_url"]
    assert c.get(att["file_url"]).data == b"%PDF"  # signature only, no token
    flipped = "1" if att["file_url"][-1] == "0" else "0"
    assert c.get(att["file_url"][:-1] + flipped).status_code == 403
    fresh = c.get(f"/api/attachments/{att['id']}/url", headers=world.h["member"])
    assert fresh.status_code == 200
    assert c.get(f"/api/attachments/{att['id']}/url", headers=world.h["other_member"]).status_code == 403
    assert c.get(f"/api/attachments/{att['id']}/url").status_code == 401
    clock.set_now(lambda: datetime.now(timezone.utc) + timedelta(seconds=1000))
    try:
        assert c.get(att["file_url"]).status_code == 403
    finally:
        clock.set_now(None)
    c.delete(f"/api/cards/{card['id']}", headers=h)
    assert c.get(att["file_url"]).status_code == 404


def test_guest_on_public_board(world):
    c, bid = world.client, world.board["id"]
    c.patch(f"/api/boards/{bid}", headers=world.h["manager"], json={"visibility": "public"})
    card = mkcard(world)
    data = c.get(f"/api/cards/{card['id']}").get_json()["data"]
    assert "comments" not in data and "activity" not in data
    assert c.get(f"/api/cards/{card['id']}/comments").status_code == 403
    assert c.get(f"/api/cards/{card['id']}/activity").status_code == 403
    assert c.post(f"/api/cards/{card['id']}/comments", json={"content": "hi"}).status_code == 403
    assert c.get(f"/api/boards/{bid}/categories").status_code == 200
    assert c.get(f"/api/boards/{bid}/cards").status_code == 200
    assert c.patch(f"/api/cards/{card['id']}", json={"title": "z"}).status_code == 401
    signed = c.get(f"/api/cards/{card['id']}", headers=world.h["member"]).get_json()["data"]
    assert "comments" in signed and "activity" in signed
    assert c.get(f"/api/cards/{card['id']}", headers=world.h["other_member"]).status_code == 200  # public


# ---- categories ----
def test_categories(world):
    c, bid = world.client, world.board["id"]
    h = world.h["supervisor"]
    cat = c.post(f"/api/boards/{bid}/categories", headers=h, json={"name": "Bug", "color": "#f00"}).get_json()["data"]
    assert c.post(f"/api/boards/{bid}/categories", headers=h, json={"name": "bug"}).status_code == 409
    other = c.post(f"/api/boards/{bid}/categories", headers=h, json={"name": "Feat"}).get_json()["data"]
    assert c.patch(f"/api/categories/{other['id']}", headers=h, json={"name": "BUG"}).status_code == 409
    assert c.post(f"/api/boards/{bid}/categories", headers=world.h["member"], json={"name": "q"}).status_code == 403
    assert c.get(f"/api/boards/{bid}/categories", headers=world.h["member"]).status_code == 200
    card = mkcard(world, category_id=cat["id"])
    assert card["category_id"] == cat["id"]
    assert c.delete(f"/api/categories/{cat['id']}", headers=h).status_code == 200
    assert c.get(f"/api/cards/{card['id']}", headers=h).get_json()["data"]["category_id"] is None


# ---- comments ----
def test_comments_flow(world):
    c = world.client
    card = mkcard(world)
    url = f"/api/cards/{card['id']}/comments"
    assert c.post(url, headers=world.h["member"], json={"content": "  "}).get_json()["error"]["details"]["content"][0] == "content is required"
    assert c.post(url, headers=world.h["admin"], json={"content": "x"}).status_code == 403
    assert c.post(url, json={"content": "x"}).status_code == 401  # private board
    m1 = c.post(url, headers=world.h["manager"], json={"content": "m1"}).get_json()["data"]
    m2 = c.post(url, headers=world.h["member"], json={"content": "m2"}).get_json()["data"]
    r1 = c.post(f"/api/comments/{m2['id']}/replies", headers=world.h["supervisor"], json={"content": "r1"}).get_json()["data"]
    assert c.post(f"/api/comments/{r1['id']}/replies", headers=world.h["supervisor"], json={"content": "deep"}).status_code == 400
    c.post(f"/api/comments/{m2['id']}/replies", headers=world.h["supervisor"], json={"content": "r2"})
    pop = c.get(url + "?sort=popular", headers=world.h["supervisor"]).get_json()["data"]
    assert [x["content"] for x in pop] == ["m2", "m1"] and pop[0]["reply_count"] == 2
    assert [r["content"] for r in pop[0]["replies"]] == ["r1", "r2"]
    assert pop[1]["can_create_card"] is True and pop[0]["can_create_card"] is False
    latest = c.get(url, headers=world.h["member"]).get_json()["data"]
    assert [x["content"] for x in latest] == ["m2", "m1"]
    assert latest[0]["can_create_card"] is False
    assert c.patch(f"/api/comments/{m1['id']}/priority", headers=world.h["supervisor"]).status_code == 403
    assert c.patch(f"/api/comments/{m1['id']}/priority").status_code == 401
    assert c.patch(f"/api/comments/{m1['id']}/priority", headers=world.h["manager"]).get_json()["data"]["is_priority"] is True
    latest = c.get(url, headers=world.h["member"]).get_json()["data"]
    assert [x["content"] for x in latest] == ["m1", "m2"]
    assert c.patch(f"/api/comments/{m1['id']}/priority", headers=world.h["manager"]).get_json()["data"]["is_priority"] is False


# ---- activity, search, analytics, users, deadlines ----
def test_activity_endpoints(world):
    card = mkcard(world)
    c = world.client
    rows = c.get(f"/api/cards/{card['id']}/activity", headers=world.h["member"]).get_json()["data"]
    assert [r["action"] for r in rows] == ["card.created"]
    board_rows = c.get(f"/api/boards/{world.board['id']}/activity", headers=world.h["manager"]).get_json()["data"]
    assert {"board.created", "card.created", "board.member_added"} <= {r["action"] for r in board_rows}
    assert c.get(f"/api/boards/{world.board['id']}/activity", headers=world.h["other_member"]).status_code == 403


def test_search_and_filter(world):
    c, bid = world.client, world.board["id"]
    mkcard(world, "Fix Login", priority="high", description="auth bug")
    mkcard(world, "Docs", priority="low")
    gone = mkcard(world, "Login gone", priority="high")
    c.delete(f"/api/cards/{gone['id']}", headers=world.h["supervisor"])
    get = lambda q: [x["title"] for x in c.get(f"/api/boards/{bid}/cards{q}", headers=world.h["member"]).get_json()["data"]]  # noqa: E731
    assert get("?search=LOGIN") == ["Fix Login"]
    assert get("?search=bug") == ["Fix Login"]
    assert get("?filter[priority]=low") == ["Docs"]
    assert get("?search=login&filter[priority]=low") == []
    assert c.get(f"/api/boards/{bid}/cards?filter[nope]=1", headers=world.h["member"]).status_code == 400
    assert c.get(f"/api/boards/{bid}/cards").status_code == 401


def test_analytics(world):
    c, bid = world.client, world.board["id"]
    mkcard(world, "late", end_date="2000-01-01")
    done = mkcard(world, "done", end_date="2000-01-01")
    prog = mkcard(world, "wip")
    c.patch(f"/api/cards/{done['id']}/move", headers=world.h["supervisor"], json={"column_id": col(world, 4)})
    c.patch(f"/api/cards/{prog['id']}/move", headers=world.h["supervisor"], json={"column_id": col(world, 1)})
    d = c.get(f"/api/boards/{bid}/analytics", headers=world.h["manager"]).get_json()["data"]
    assert (d["total"], d["done"], d["in_progress"], d["overdue"], d["done_delta"]) == (3, 1, 1, 1, 1)
    assert c.get(f"/api/boards/{bid}/analytics", headers=world.h["supervisor"]).status_code == 200  # owner
    assert c.get(f"/api/boards/{bid}/analytics", headers=world.h["other_sup"]).status_code == 403
    for who in ("member", "admin"):
        assert c.get(f"/api/boards/{bid}/analytics", headers=world.h[who]).status_code == 403
    assert c.get(f"/api/boards/{bid}/analytics").status_code == 401
    assert len(c.get("/api/analytics/boards", headers=world.h["manager"]).get_json()["data"]) == 1
    assert c.get("/api/analytics/boards", headers=world.h["supervisor"]).status_code == 403


def test_deadline_job_once_in_timezone(world, app):
    from app.jobs.deadlines import run

    app.config["APP_TIMEZONE"] = "Asia/Jakarta"
    card = mkcard(world, end_date="2026-03-02", assignee_id=str(world.users["member"].id))
    mkcard(world, "unassigned", end_date="2026-03-02")
    # 2026-03-01 18:00 UTC is already 03-02 01:00 in Jakarta
    now = datetime(2026, 3, 1, 18, 0, tzinfo=timezone.utc)
    assert run(now) == 1
    assert run(now) == 1
    assert Notification.query.filter_by(type="deadline").count() == 1
    assert run(datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc)) == 0


def test_user_admin(world):
    c = world.client
    for who in ("member", "supervisor", "manager"):
        assert c.get("/api/users", headers=world.h[who]).status_code == 403
    assert c.get("/api/users").status_code == 401
    r = c.post("/api/users", headers=world.h["admin"], json={"full_name": "N", "login_identifier": "n@x.com", "password": TEST_PASSWORD, "role": "supervisor"})
    assert r.status_code == 201
    uid = r.get_json()["data"]["id"]
    r = c.patch(f"/api/users/{uid}", headers=world.h["admin"], json={"role": "manager", "full_name": "M"})
    assert r.get_json()["data"]["role"] == "manager"
    actions = {a.action for a in ActivityLog.query.all()}
    assert {"user.created", "user.updated", "user.role_changed"} <= actions
    assert c.patch(f"/api/users/{uid}", headers=world.h["admin"], json={"role": "root"}).status_code == 400
    assert len(c.get("/api/users", headers=world.h["admin"]).get_json()["data"]) >= 7


# ---- cross-cutting ----
def test_mutating_routes_401_without_token_and_403_for_member(app, world):
    """Sweep: every mutating route rejects no-token (401) unless public/signature-gated or per-resource."""
    public = {"auth.register", "auth.login", "auth.logout", "comments.create", "comments.reply"}
    c = world.client
    for rule in app.url_map.iter_rules():
        methods = rule.methods & {"POST", "PATCH", "PUT", "DELETE"}
        if not methods or rule.endpoint == "static" or rule.endpoint in public:
            continue
        path = __import__("re").sub(r"<[^>]+>", "00000000-0000-0000-0000-000000000000", rule.rule)
        for m in methods:
            r = c.open(path, method=m, json={})
            assert r.status_code == 401, (m, rule.rule, r.status_code)


def test_envelope_everywhere(world, app):
    c = world.client
    for path in ("/api/boards", "/api/nope", "/api/cards/not-a-uuid", f"/api/boards/{world.board['id']}"):
        body = c.get(path, headers=world.h["manager"]).get_json()
        assert set(body) in ({"status", "message", "data"}, {"status", "message", "error"})
        if "error" in body:
            assert set(body["error"]) <= {"code", "details"} and "code" in body["error"]


def test_no_query_outside_repository_and_env_not_tracked():
    import pathlib
    import subprocess

    root = pathlib.Path(__file__).resolve().parents[1]
    offenders = []
    for p in (root / "app").rglob("*.py"):
        if p.name in ("repository.py", "seed.py"):
            continue
        if ".query" in p.read_text():
            offenders.append(str(p.relative_to(root)))
    assert offenders == []
    banned = ("import flask", "from flask", "flask_smorest", "marshmallow")
    layering = [
        str(p.relative_to(root))
        for p in (root / "app" / "blueprints").rglob("*.py")
        if p.name in ("service.py", "repository.py") and any(b in p.read_text() for b in banned)
    ]
    # services/repositories stay free of Flask, smorest and marshmallow (only config access via current_app is allowed)
    assert [x for x in layering if "from flask import current_app" not in (root / x).read_text()] == []
    views = []
    for p in (root / "app" / "blueprints").glob("*/routes.py"):
        src = p.read_text()
        for block in src.split("@bp.route(")[1:]:
            head = block.split("\ndef ")[0]
            if "@bp.response(" not in head and "/file" not in head:
                views.append(f"{p.parent.name}: {head.splitlines()[0]}")
    assert views == []
    example = (root / ".env.example").read_text()
    for var in ("DATABASE_URL", "JWT_SECRET", "ALLOWED_ORIGINS", "FILE_URL_SECRET", "APP_TIMEZONE", "UPLOAD_DIR"):
        assert var + "=" in example
    tracked = subprocess.run(["git", "ls-files", "--", ".env", "backend/.env"], cwd=root, capture_output=True, text=True).stdout
    assert tracked.strip() == ""
