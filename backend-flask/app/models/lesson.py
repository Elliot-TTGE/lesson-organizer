from app.db import db
from app.models.lesson_student import LessonStudent
from app.models.quiz import Quiz

class Lesson(db.Model):
    __tablename__ = 'lesson'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(db.DateTime, nullable=False)
    plan = db.Column(db.String)
    concepts = db.Column(db.String)
    created_date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.String)
    
    students = db.relationship('Student', secondary='lesson_student', back_populates='lessons')
    quizzes = db.relationship('Quiz', back_populates='lesson')