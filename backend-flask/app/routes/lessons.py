from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import db
from app.models.lesson import Lesson
from app.models.schema import LessonSchema
from app.models.student import Student
from app.models.quiz import Quiz
from app.routes.utils import response_wrapper
from datetime import datetime, timezone, timedelta

lessons_bp = Blueprint('lessons', __name__)

@lessons_bp.route('/lessons', methods=['GET'])
@jwt_required()
@response_wrapper
def get_lessons():
    initial_date_str = request.args.get('initial_date')
    range_length = request.args.get('range_length', type=int, default=7)

    if initial_date_str:
        print(initial_date_str, flush=True)
        try:
            initial_date = datetime.fromisoformat(initial_date_str)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use ISO format (YYYY-MM-DD)."}), 400
    else:
        initial_date = datetime.now(timezone.utc)

    end_date = initial_date + timedelta(days=range_length)

    lessons = Lesson.query.filter(Lesson.datetime >= initial_date, Lesson.datetime < end_date).all()
    lesson_schema = LessonSchema(many=True)
    return lesson_schema.dump(lessons)

@lessons_bp.route('/lessons', methods=['POST'])
@jwt_required()
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
@jwt_required()
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
@jwt_required()
@response_wrapper
def delete_lesson(id):
    lesson = Lesson.query.get_or_404(id)
    db.session.delete(lesson)
    db.session.commit()
    return '', 204