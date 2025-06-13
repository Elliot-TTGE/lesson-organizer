from app.models.base_model import BaseModel
from app.db import db

class Curriculum(BaseModel):
    __tablename__ = 'curriculum'

    name = db.Column(db.String, nullable=False)