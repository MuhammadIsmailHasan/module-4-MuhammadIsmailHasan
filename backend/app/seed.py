"""Dev-only helper: one user per role. Registered as `flask seed-users`.

No credential lives in the code: the password comes from SEED_PASSWORD, or a random
one is generated and printed once. Refuses to run unless APP_ENV is development or testing.
"""
import os
import secrets

import click
from argon2 import PasswordHasher

from app.extensions import db
from app.models import User

ROLES = ("member", "supervisor", "manager", "admin")
SEED_ENVS = ("development", "testing")
_hasher = PasswordHasher()


def create_users_of_each_role(password, domain="example.com"):
    users = {}
    for role in ROLES:
        login = f"{role}@{domain}"
        user = User.query.filter(db.func.lower(User.login_identifier) == login).first()
        if user is None:
            user = User(
                full_name=role.capitalize(),
                login_identifier=login,
                password_hash=_hasher.hash(password),
                role=role,
            )
            db.session.add(user)
        users[role] = user
    db.session.commit()
    return users


def register_cli(app):
    @app.cli.command("seed-users")
    def seed_users():
        """Create one user per role (development/testing only)."""
        if app.config["APP_ENV"] not in SEED_ENVS:
            raise click.ClickException("seed-users only runs when APP_ENV is development or testing")
        password = os.environ.get("SEED_PASSWORD") or secrets.token_urlsafe(16)
        generated = not os.environ.get("SEED_PASSWORD")
        create_users_of_each_role(password)
        click.echo("Seeded users: " + ", ".join(f"{r}@example.com" for r in ROLES))
        if generated:
            click.echo(f"Generated password (shown once): {password}")
