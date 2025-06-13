from app.models.base_model import BaseModel
from app.db import db

class Unit(BaseModel):
    __tablename__ = "unit"

    name = db.Column(db.String, nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey("level.id"), nullable=False)

    # Relationships
    level = db.relationship("Level", back_populates="units")
    quizzes = db.relationship("Quiz", back_populates="unit", cascade="all, delete-orphan")