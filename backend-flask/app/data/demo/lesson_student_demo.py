from app.main import db
from app.models.student import Student
from app.models.lesson import Lesson
import random

def assign_students_to_lessons():
    students = Student.query.all()
    lessons = Lesson.query.all()
    student_ids = [student.id for student in students]
    assigned_students = set()

    for lesson in lessons:
        lesson_students = random.sample(student_ids, min(len(student_ids), random.randint(3, 5)))
        for student_id in lesson_students:
            student = Student.query.get(student_id)
            if student not in lesson.students:
                lesson.students.append(student)
                assigned_students.add(student_id)

    # Ensure every student is assigned at least once
    unassigned_students = set(student_ids) - assigned_students
    for student_id in unassigned_students:
        lesson = random.choice(lessons)
        student = Student.query.get(student_id)
        if student not in lesson.students:
            lesson.students.append(student)

    db.session.commit()