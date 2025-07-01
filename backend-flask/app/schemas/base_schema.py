from marshmallow import post_dump, EXCLUDE, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow_sqlalchemy.fields import Nested
from app.db import db
import re

ISO_DATETIME_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')

class BaseSchema(SQLAlchemyAutoSchema):
    id = fields.Integer(dump_only=True)
    created_date = fields.DateTime(dump_only=True)
    updated_date = fields.DateTime(dump_only=True)
    class Meta:
        abstract = True
        unknown = EXCLUDE
        sqla_session = db.session
        load_instance = True
        include_relationships = True

    @post_dump
    def add_utc_suffix(self, data, **kwargs):
        # Add 'Z' to all datetime fields that are present and not already suffixed
        for key, value in data.items():
            if (
                isinstance(value, str)
                and ISO_DATETIME_RE.match(value)
                and not value.endswith('Z')
            ):
                data[key] = value + 'Z'
        return data