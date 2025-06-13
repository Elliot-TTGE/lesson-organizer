from app.models.base_model import BaseModel
from app.db import db

class Level(BaseModel):
    __tablename__ = "level"

    name = db.Column(db.String, nullable=False)
    curriculum_id = db.Column(db.Integer, db.ForeignKey("curriculum.id"), nullable=False)

    # Relationships
    curriculum = db.relationship("Curriculum", back_populates="levels")
    student_level_history = db.relationship("StudentLevelHistory", back_populates="level", cascade="all, delete-orphan")
    units = db.relationship("Unit", back_populates="level", cascade="all, delete-orphan")