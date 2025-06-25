from datetime import datetime, timezone
from app.db import db

class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    created_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))