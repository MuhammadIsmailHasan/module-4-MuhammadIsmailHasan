"""Dev/test helper: one user per role. Registered as `flask seed-users`."""
import click
from argon2 import PasswordHasher

from app.extensions import db
from app.models import User

ROLES = ("member", "supervisor", "manager", "admin")
_hasher = PasswordHasher()


def create_users_of_each_role(password="REMOVED", domain="example.com"):
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
        """Create one user per role (password: REMOVED)."""
        create_users_of_each_role()
        click.echo("Seeded users: " + ", ".join(ROLES))
