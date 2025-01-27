from app.main import db
from datetime import datetime

lesson_student = db.Table('lesson_student',
    db.Column('lesson_id', db.Integer, db.ForeignKey('lesson.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True)
)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    plan = db.Column(db.Text, nullable=False)
    concepts_taught = db.Column(db.Text, nullable=True)
    additional_notes = db.Column(db.Text, nullable=True)
    students = db.relationship('Student', secondary=lesson_student, back_populates='lessons')