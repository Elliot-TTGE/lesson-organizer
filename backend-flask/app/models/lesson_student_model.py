from app.models.base_model import BaseModel
from app.db import db

class LessonStudent(BaseModel):
    __tablename__ = 'lesson_student'
    
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False)