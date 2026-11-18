from datetime import timedelta

from flask import current_app

from app.blueprints.analytics import repository as repo
from app.blueprints.boards import service as boards
from app.common import clock
from app.common.errors import Forbidden
from app.common.ids import to_uuid


def _shape(row):
    board_id, name, total, done, in_progress, overdue, delta = row
    return {
        "board_id": str(board_id),
        "name": name,
        "total": int(total),
        "done": int(done),
        "in_progress": int(in_progress),
        "overdue": int(overdue),
        "done_delta": int(delta),
    }


def _args():
    now = clock.now()
    return clock.today(current_app.config["APP_TIMEZONE"]), now - timedelta(days=7)


def board_analytics(actor, board_id):
    board = boards.load_board(actor, board_id)
    if not (actor.role == "manager" or (actor.role == "supervisor" and boards.is_owner(actor, board))):
        raise Forbidden("Analytics not available for this role")
    today, week_ago = _args()
    return _shape(repo.summaries(today, week_ago, board.id)[0])


def all_boards(actor):
    if actor.role != "manager":
        raise Forbidden("Manager only")
    today, week_ago = _args()
    return [_shape(r) for r in repo.summaries(today, week_ago)]
