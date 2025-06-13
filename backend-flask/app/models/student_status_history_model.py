from app.models.base_model import BaseModel
from app.db import db

class StudentStatusHistory(BaseModel):
    __tablename__ = "student_status_history"

    student_id = db.Column(db.Integer, db.ForeignKey("student.id", ondelete="CASCADE"), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey("student_status.id", ondelete="CASCADE"), nullable=False)
    changed_at = db.Column(db.DateTime, nullable=False)

    # Relationships
    student = db.relationship("Student", back_populates="status_history")
    status = db.relationship("StudentStatus", back_populates="status_history")

