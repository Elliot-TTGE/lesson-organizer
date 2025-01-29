from app.main import db
from app.models.student import Student
from app.models.lesson import Lesson

def assign_students_to_lessons():
    students = Student.query.all()
    lessons = Lesson.query.all()
    for lesson in lessons:
        for student in students:
            if student not in lesson.students:
                lesson.students.append(student)
    db.session.commit()