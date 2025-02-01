from app.db import db
from app.models.lesson_student import LessonStudent
from app.models.quiz import Quiz

class Lesson(db.Model):
    __tablename__ = 'lesson'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(db.DateTime, nullable=False)
    plan = db.Column(db.String, nullable=False)
    concepts = db.Column(db.String, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.String)
    
    lesson_students = db.relationship('LessonStudent', back_populates='lesson', overlaps="students")
    students = db.relationship('Student', secondary='lesson_student', back_populates='lessons', overlaps="lesson_students,lesson")
    quizzes = db.relationship('Quiz', back_populates='lesson')