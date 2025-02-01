from app.db import db
from app.models.lesson_student import LessonStudent
from app.models.quiz import Quiz
from app.models.level import Level

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('active', 'inactive', 'hold', 'trial', name='student_status'), nullable=False)
    
    lesson_students = db.relationship('LessonStudent', back_populates='student')
    lessons = db.relationship('Lesson', secondary='lesson_student', back_populates='students')
    quizzes = db.relationship('Quiz', back_populates='student')
    levels = db.relationship('Level', back_populates='student')