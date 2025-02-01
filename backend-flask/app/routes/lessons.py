from flask import Blueprint, jsonify, request
from app.db import db
from app.models.lesson import Lesson
from app.models.student import Student
from app.models.schema import LessonSchema

lessons_bp = Blueprint('lessons', __name__)

@lessons_bp.route('/lessons', methods=['GET'])
def get_lessons():
    lessons = Lesson.query.all()
    lesson_schema = LessonSchema(many=True)
    return jsonify(lesson_schema.dump(lessons))

@lessons_bp.route('/lessons', methods=['POST'])
def create_lesson():
    data = request.get_json()
    lesson_schema = LessonSchema()
    lesson_data = lesson_schema.load(data)

    # Create or get students
    student_names = lesson_data.pop('students')
    students = []
    for name in student_names:
        student = Student.query.filter_by(name=name).first()
        if not student:
            student = Student(name=name)
            db.session.add(student)
        students.append(student)

    # Create lesson
    new_lesson = Lesson(
        datetime=lesson_data['datetime'],
        plan=lesson_data['plan'],
        concepts_taught=lesson_data.get('concepts_taught', ''),
        additional_notes=lesson_data.get('additional_notes', '')
    )
    new_lesson.students.extend(students)
    db.session.add(new_lesson)
    db.session.commit()

    return jsonify(lesson_schema.dump(new_lesson)), 201