from marshmallow import Schema, fields, post_dump, EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.db import db
import re

ISO_DATETIME_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')

class BaseSchema(SQLAlchemyAutoSchema):
    class Meta:
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