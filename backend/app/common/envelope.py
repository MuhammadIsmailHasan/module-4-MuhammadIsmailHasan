"""Envelope schemas: { status, message, data } for success, { status, message, error } for failure."""
import marshmallow as ma
from marshmallow import fields

_cache = {}


class ErrorDetailSchema(ma.Schema):
    code = fields.String(metadata={"description": "Machine-readable error code"})
    message = fields.String(metadata={"description": "Human-readable error message"})


class ErrorEnvelopeSchema(ma.Schema):
    status = fields.Integer(metadata={"description": "HTTP status code"})
    message = fields.String(metadata={"description": "Human-readable message"})
    error = fields.Nested(ErrorDetailSchema)


class NullEnvelopeSchema(ma.Schema):
    status = fields.Integer(metadata={"description": "HTTP status code"})
    message = fields.String()
    data = fields.Raw(allow_none=True, metadata={"description": "Always null"})


def envelope(data_schema, many=False):
    """Return (and cache) a schema wrapping data_schema in the success envelope."""
    key = (data_schema, many)
    if key not in _cache:
        base = data_schema.__name__.removesuffix("Schema")
        name = f"{base}{'List' if many else ''}EnvelopeSchema"
        _cache[key] = type(
            name,
            (ma.Schema,),
            {
                "status": fields.Integer(metadata={"description": "HTTP status code"}),
                "message": fields.String(metadata={"description": "Human-readable message"}),
                "data": fields.Nested(data_schema, many=many, allow_none=True),
            },
        )
    return _cache[key]
