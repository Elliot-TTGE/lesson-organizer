from app.models.base_model import BaseModel
from app.db import db

class StudentLessonQuiz(BaseModel):
    __tablename__ = "student_lesson_quiz"

    student_id = db.Column(db.Integer, db.ForeignKey("student.id", ondelete="CASCADE"), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lesson.id", ondelete="CASCADE"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id", ondelete="SET NULL"), nullable=True)
    points = db.Column(db.Integer)
    notes = db.Column(db.String)

    # Relationships
    student = db.relationship("Student", back_populates="quizzes")
    lesson = db.relationship("Lesson", back_populates="student_lesson_quizzes")
    quiz = db.relationship("Quiz", back_populates="student_lesson_quizzes")