from app.db import db

class LessonStudent(db.Model):
    __tablename__ = 'lesson_student'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
    
    lesson = db.relationship('Lesson', back_populates='lesson_students')
    student = db.relationship('Student', back_populates='lesson_students')