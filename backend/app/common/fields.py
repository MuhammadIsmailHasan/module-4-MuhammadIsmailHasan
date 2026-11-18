"""Shared marshmallow pieces: base schema, trimmed text, error messages."""
import marshmallow as ma
from marshmallow import fields


class BaseSchema(ma.Schema):
    class Meta:
        unknown = ma.EXCLUDE


class Text(fields.String):
    """Trimmed, non-empty string; messages name the field (for example 'content is required')."""

    def __init__(self, *, max_length=None, min_length=None, allow_blank=False, strip=True, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length
        self.min_length = min_length
        self.allow_blank = allow_blank
        self.strip = strip
        if max_length:
            self.metadata = {**self.metadata, "maxLength": max_length}

    def make_error(self, key, **kwargs):
        if key in ("required", "null"):
            raise ma.ValidationError(f"{self.name} is required")
        return super().make_error(key, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, str):
            raise ma.ValidationError(f"{attr} must be text")
        if self.strip:
            value = value.strip()
        if not value and not self.allow_blank:
            raise ma.ValidationError(f"{attr} is required")
        if self.min_length and len(value) < self.min_length:
            raise ma.ValidationError(f"{attr} must be at least {self.min_length} characters")
        if self.max_length and len(value) > self.max_length:
            raise ma.ValidationError(f"{attr} must be at most {self.max_length} characters")
        return value
