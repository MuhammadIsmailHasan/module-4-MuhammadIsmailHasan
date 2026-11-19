"""Properties 3, 4, 5 and the Board_Access matrix (tasks 4.2, 4.3, 14.2, 14.3)."""
import pytest
from hypothesis import given, strategies as st

from helpers import PROP, RELATIONS, STAFF, UUID0, Env


def can_access(rel, vis):
    return vis == "public" or rel in {"manager", "admin", "owner", "sup_member", "member"}


def denied(rel):
    return 401 if rel == "guest" else 403


def oracle(action, rel, vis):
    acc = can_access(rel, vis)
    if action in ("get_board", "list_categories", "search", "attachment_url"):
        return 200 if acc else denied(rel)
    if action in ("create_column", "create_category"):
        if rel == "guest":
            return 401
        if not acc:
            return 403
        return 201 if rel in STAFF else 403
    if action == "comment":
        if not acc:
            return denied(rel)
        return 201 if rel in {"manager", "owner", "sup_member", "sup_other", "member", "member_other"} else 403
    if action == "analytics":
        if rel == "guest":
            return 401
        return 200 if rel in ("manager", "owner") else 403
    if action == "activity":
        if not acc:
            return denied(rel)
        return 403 if rel == "guest" else 200
    raise AssertionError(action)


ACTIONS = ("get_board", "list_categories", "search", "attachment_url", "create_column", "create_category", "comment", "analytics", "activity")


def call(env, action, rel, ids):
    c, h = env.c, env.h[rel]
    if action == "get_board":
        return c.get(f"/api/boards/{env.bid}", headers=h)
    if action == "list_categories":
        return c.get(f"/api/boards/{env.bid}/categories", headers=h)
    if action == "search":
        return c.get(f"/api/boards/{env.bid}/cards", headers=h)
    if action == "attachment_url":
        return c.get(f"/api/attachments/{ids['att']}/url", headers=h)
    if action == "create_column":
        return c.post(f"/api/boards/{env.bid}/columns", headers=h, json={"name": "C"})
    if action == "create_category":
        return c.post(f"/api/boards/{env.bid}/categories", headers=h, json={"name": "K"})
    if action == "comment":
        return c.post(f"/api/cards/{ids['card']}/comments", headers=h, json={"content": "x"})
    if action == "analytics":
        return c.get(f"/api/boards/{env.bid}/analytics", headers=h)
    if action == "activity":
        return c.get(f"/api/cards/{ids['card']}/activity", headers=h)


@pytest.mark.parametrize("vis", ["public", "private"])
def test_board_access_matrix_exhaustive(client, vis):
    """Properties 3, 4, 5 and tasks 4.3, 14.3: every relation x action on public and private boards."""
    for rel in RELATIONS:
        for action in ACTIONS:
            env = Env(client, vis)
            card = env.card()
            att = client.post(f"/api/cards/{card['id']}/attachments", headers=env.h["manager"], json={"url": "https://e.com/x"}).get_json()["data"]
            r = call(env, action, rel, {"card": card["id"], "att": att["id"]})
            assert r.status_code == oracle(action, rel, vis), (vis, rel, action, r.get_json())
            body = r.get_json()
            assert body["status"] is (r.status_code < 400)


@PROP
@given(rel=st.sampled_from(RELATIONS), vis=st.sampled_from(["public", "private"]), action=st.sampled_from(ACTIONS))
def test_property_4_board_access_function(client, rel, vis, action):
    env = Env(client, vis)
    card = env.card()
    att = client.post(f"/api/cards/{card['id']}/attachments", headers=env.h["manager"], json={"url": "https://e.com/x"}).get_json()["data"]
    assert call(env, action, rel, {"card": card["id"], "att": att["id"]}).status_code == oracle(action, rel, vis)


@PROP
@given(rel=st.sampled_from(RELATIONS), vis=st.sampled_from(["public", "private"]))
def test_property_5_401_vs_403_vs_404(client, rel, vis):
    env = Env(client, vis)
    # unknown or malformed ids are 404 for any caller who passes the role gate
    for path in (f"/api/boards/{UUID0}", "/api/boards/not-a-uuid"):
        r = client.get(path, headers=env.h[rel])
        assert r.status_code == 404
    # a soft-deleted board is 404 for everyone, including its owner and managers
    client.delete(f"/api/boards/{env.bid}", headers=env.h["manager"])
    assert client.get(f"/api/boards/{env.bid}", headers=env.h[rel]).status_code == 404
    # no Token on a protected endpoint is 401, a Token without the role is 403
    assert client.get("/api/notifications").status_code == 401
    assert client.get("/api/users", headers=env.h["manager"]).status_code == 403
    assert client.get("/api/users").status_code == 401


@PROP
@given(rel=st.sampled_from(RELATIONS), vis=st.sampled_from(["public", "private"]))
def test_property_34_board_list_visibility(client, rel, vis):
    env = Env(client, vis)
    other = client.post("/api/boards", headers=env.h["manager"], json={"name": "P", "visibility": "public"}).get_json()["data"]
    gone = client.post("/api/boards", headers=env.h["manager"], json={"name": "G", "visibility": "public"}).get_json()["data"]
    client.delete(f"/api/boards/{gone['id']}", headers=env.h["manager"])
    ids = {b["id"] for b in client.get("/api/boards", headers=env.h[rel]).get_json()["data"]}
    expected = {other["id"]}
    if can_access(rel, vis):
        expected.add(env.bid)
    assert ids == expected
