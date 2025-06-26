from app.models.base_model import BaseModel
from app.db import db

class Student(BaseModel):
    __tablename__ = 'student'

    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    date_started = db.Column(db.DateTime)
    classes_per_week = db.Column(db.Integer)
    notes_general = db.Column(db.String)
    notes_strengths = db.Column(db.String)
    notes_weaknesses = db.Column(db.String)
    notes_future = db.Column(db.String)

    # Relationships
    lessons = db.relationship('Lesson', secondary='lesson_student', back_populates='students')
    status_history = db.relationship('StudentStatusHistory', cascade="all, delete-orphan")
    level_history = db.relationship('StudentLevelHistory', cascade="all, delete-orphan")
    quizzes = db.relationship('StudentLessonQuiz', cascade="all, delete-orphan")