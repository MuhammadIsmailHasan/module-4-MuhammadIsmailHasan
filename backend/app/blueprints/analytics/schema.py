from marshmallow import fields

from app.common.fields import BaseSchema


class AnalyticsSchema(BaseSchema):
    board_id = fields.UUID()
    name = fields.String()
    total = fields.Integer()
    done = fields.Integer()
    in_progress = fields.Integer()
    overdue = fields.Integer(metadata={"description": "Past end_date and not in Done"})
    done_delta = fields.Integer(metadata={"description": "Cards in Done updated in the last 7 days"})
