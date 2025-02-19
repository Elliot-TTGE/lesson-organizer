from app.db import db

class Quiz(db.Model):
    __tablename__ = 'quiz'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    score = db.Column(db.Float, nullable=False)
    notes = db.Column(db.String)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    
    lesson = db.relationship('Lesson', back_populates='quizzes')
    student = db.relationship('Student', back_populates='quizzes')