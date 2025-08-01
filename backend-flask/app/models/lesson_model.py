from app.models.base_model import BaseModel
from app.db import db

class Lesson(BaseModel):
    __tablename__ = "lesson"

    datetime = db.Column(db.DateTime, nullable=False)
    plan = db.Column(db.String)
    concepts = db.Column(db.String)
    notes = db.Column(db.String)

    # Relationships
    students = db.relationship(
        "Student",
        secondary="lesson_student",
        back_populates="lessons"
    )