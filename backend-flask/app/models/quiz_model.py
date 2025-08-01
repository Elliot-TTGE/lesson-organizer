from app.models.base_model import BaseModel
from app.db import db

class Quiz(BaseModel):
    __tablename__ = "quiz"

    name = db.Column(db.String, nullable=False)
    max_points = db.Column(db.Integer, nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey("unit.id"), nullable=True)

    # Relationships
    unit = db.relationship("Unit", back_populates="quizzes")