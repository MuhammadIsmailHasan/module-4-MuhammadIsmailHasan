"""Shared builders for the property-based tests."""
import itertools

from argon2 import PasswordHasher
from hypothesis import HealthCheck, settings

from app.common import clock
from app.common.auth import issue_token
from app.extensions import db
from app.models import User

PROP = settings(max_examples=100, deadline=None, suppress_health_check=list(HealthCheck))
_hash = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1).hash("unused-in-property-tests")
_n = itertools.count()
UUID0 = "00000000-0000-0000-0000-000000000000"


def reset_db():
    db.session.remove()
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()


def mkuser(role):
    n = next(_n)
    u = User(full_name=role, username=f"{role}{n}", email=f"{role}{n}@t.test", password_hash=_hash, role=role)
    db.session.add(u)
    db.session.commit()
    return u


def hdr(user):
    return {"Authorization": f"Bearer {issue_token(user.id, user.role)}"}


class Ticker:
    """Strictly increasing injectable clock so created_at ordering is deterministic."""

    def __init__(self):
        from datetime import datetime, timedelta, timezone

        self.t = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.step = timedelta(seconds=1)

    def __call__(self):
        self.t += self.step
        return self.t

    def __enter__(self):
        clock.set_now(self)
        return self

    def __exit__(self, *exc):
        clock.set_now(None)


RELATIONS = ("guest", "manager", "admin", "owner", "sup_member", "sup_other", "member", "member_other")
STAFF = {"manager", "admin", "owner", "sup_member"}


class Env:
    """One board plus one user per relationship to it. Call build() once per example."""

    def __init__(self, client, visibility="private"):
        reset_db()
        self.c = client
        u = self.users = {
            "manager": mkuser("manager"),
            "admin": mkuser("admin"),
            "owner": mkuser("supervisor"),
            "sup_member": mkuser("supervisor"),
            "sup_other": mkuser("supervisor"),
            "member": mkuser("member"),
            "member_other": mkuser("member"),
        }
        self.h = {k: hdr(v) for k, v in u.items()}
        self.h["guest"] = {}
        b = client.post("/api/boards", headers=self.h["manager"], json={"name": "B", "visibility": visibility}).get_json()["data"]
        self.board = b
        self.bid = b["id"]
        self.cols = [c["id"] for c in b["columns"]]
        client.patch(f"/api/boards/{self.bid}", headers=self.h["manager"], json={"owner_id": str(u["owner"].id)})
        for who in ("sup_member", "member"):
            client.post(f"/api/boards/{self.bid}/members", headers=self.h["manager"], json={"user_id": str(u[who].id)})

    def card(self, who="manager", col=0, **kw):
        r = self.c.post(f"/api/columns/{self.cols[col]}/cards", headers=self.h[who], json={"title": "t", **kw})
        assert r.status_code == 201, r.get_json()
        return r.get_json()["data"]

    def uid(self, who):
        return str(self.users[who].id)
