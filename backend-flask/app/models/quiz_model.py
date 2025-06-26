from app.models.base_model import BaseModel
from app.db import db

class Quiz(BaseModel):
    __tablename__ = "quiz"

    name = db.Column(db.String, nullable=False)
    max_points = db.Column(db.Integer, nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey("unit.id"), nullable=True)

    # Relationships
    unit = db.relationship("Unit", back_populates="quizzes")
    lessons = db.relationship(
        "Lesson",
        secondary="student_lesson_quiz",
        primaryjoin="Quiz.id==StudentLessonQuiz.quiz_id",
        secondaryjoin="Lesson.id==StudentLessonQuiz.lesson_id",
        back_populates="quizzes",
        overlaps="students"
    )
    students = db.relationship(
        "Student",
        secondary="student_lesson_quiz",
        primaryjoin="Quiz.id==StudentLessonQuiz.quiz_id",
        secondaryjoin="Student.id==StudentLessonQuiz.student_id",
        overlaps="lessons,quizzes"
    )