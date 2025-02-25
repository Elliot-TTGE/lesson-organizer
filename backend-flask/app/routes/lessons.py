from flask import Blueprint, request, jsonify
from app.db import db
from app.models.lesson import Lesson
from app.models.schema import LessonSchema
from app.models.student import Student
from app.models.quiz import Quiz
from app.routes.utils import response_wrapper
from datetime import datetime, timezone

lessons_bp = Blueprint('lessons', __name__)

@lessons_bp.route('/lessons', methods=['GET'])
@response_wrapper
def get_lessons():
    lessons = Lesson.query.all()
    lesson_schema = LessonSchema(many=True)
    return lesson_schema.dump(lessons)

@lessons_bp.route('/lessons', methods=['POST'])
@response_wrapper
def create_lesson():
    data = request.get_json()
    lesson_schema = LessonSchema()
    lesson = lesson_schema.load(data)
    new_lesson = Lesson(
        datetime=lesson['datetime'],
        plan=lesson['plan'],
        concepts=lesson['concepts'],
        created_date=datetime.now(timezone.utc),
        notes=lesson['notes']
    )
    db.session.add(new_lesson)
    db.session.commit()
    return lesson_schema.dump(new_lesson), 201

@lessons_bp.route('/lessons/<int:id>', methods=['PUT'])
@response_wrapper
def update_lesson(id):
    lesson = Lesson.query.get_or_404(id)
    data = request.get_json()
    lesson_schema = LessonSchema()
    updated_data = lesson_schema.load(data, partial=True)
    
    if 'datetime' in updated_data:
        lesson.datetime = updated_data['datetime']
    if 'plan' in updated_data:
        lesson.plan = updated_data['plan']
    if 'concepts' in updated_data:
        lesson.concepts = updated_data['concepts']
    if 'notes' in updated_data:
        lesson.notes = updated_data['notes']
    
    if 'students' in data:
        lesson.students = [Student.query.get(student['id']) for student in data['students']]
    if 'quizzes' in data:
        lesson.quizzes = [Quiz.query.get(quiz['id']) for quiz in data['quizzes']]
    
    db.session.commit()
    return lesson_schema.dump(lesson), 200

@lessons_bp.route('/lessons/<int:id>', methods=['DELETE'])
@response_wrapper
def delete_lesson(id):
    lesson = Lesson.query.get_or_404(id)
    db.session.delete(lesson)
    db.session.commit()
    return '', 204