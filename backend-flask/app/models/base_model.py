from app.db import db

class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    created_date = db.Column(db.Datetime, nullable=False)
    updated_date = db.Column(db.Datetime, nullable=False)