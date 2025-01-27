from app.main import db

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    lessons = db.relationship('Lesson', secondary='lesson_student', back_populates='students')