from app.models.base_model import BaseModel
from app.db import db

class StudentLevelHistory(BaseModel):
    __tablename__ = "student_level_history"

    student_id = db.Column(db.Integer, db.ForeignKey("student.id", ondelete="CASCADE"), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey("level.id", ondelete="CASCADE"), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)