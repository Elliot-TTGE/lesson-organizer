from app.main import db
from app.models.student import Student
from app.models.lesson import Lesson

def assign_students_to_lessons():
    students = Student.query.all()
    lessons = Lesson.query.all()
    for lesson in lessons:
        lesson.students.extend(students)
    db.session.commit()