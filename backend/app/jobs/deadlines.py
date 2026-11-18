"""Daily deadline job: one `deadline` notification per assigned card due today."""
import click
from flask import current_app

from app.blueprints.notifications import repository as repo
from app.common import clock
from app.extensions import db


def run(now=None):
    if now is not None:
        clock.set_now(lambda: now)
    try:
        today = clock.today(current_app.config["APP_TIMEZONE"])
        cards = repo.cards_due(today)
        for card in cards:
            repo.insert_ignore(card.assignee_id, card.id, "deadline", today)
        db.session.commit()
        return len(cards)
    finally:
        if now is not None:
            clock.set_now(None)


def register_cli(app):
    @app.cli.command("notify-deadlines")
    def notify_deadlines():
        """Create deadline notifications for cards due today (run daily)."""
        click.echo(f"Processed {run()} due cards")
