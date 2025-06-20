"""
Routes for managing lessons.

Blueprint: lessons_bp

Routes:
-------

GET /lessons
    Retrieves a list of lessons within a specified date range.
    Query Parameters:
        - initial_date (str, optional): The start date in ISO format (YYYY-MM-DD). Defaults to current UTC date if not provided.
        - range_length (int, optional): Number of days in the range. Defaults to 7.
    Response:
        - 200: List of lessons serialized by LessonSchema.
        - 400: Error if initial_date is not in ISO format.

POST /lessons
    Creates a new lesson.
    Request JSON Body:
        {
            "lesson": { ... },         # Lesson fields as defined in LessonSchema
            "student_ids": [1, 2, ...] # Optional list of student IDs to associate with the lesson
        }
    Response:
        - 201: The created lesson serialized by LessonSchema.

PUT /lessons/<int:id>
    Updates an existing lesson.
    URL Parameters:
        - id (int): ID of the lesson to update.
    Request JSON Body:
        {
            "lesson": { ... },         # Fields to update as defined in LessonSchema
            "student_ids": [1, 2, ...] # Optional list of student IDs to associate with the lesson
        }
    Response:
        - 200: The updated lesson serialized by LessonSchema.
        - 404: If lesson with given ID does not exist.

DELETE /lessons/<int:id>
    Deletes a lesson.
    URL Parameters:
        - id (int): ID of the lesson to delete.
    Response:
        - 204: No content on successful deletion.
        - 404: If lesson with given ID does not exist.

Formatting Requirements:
------------------------
- Dates must be provided in ISO format (YYYY-MM-DD).
- Request bodies for POST and PUT must be JSON with "lesson" and optional "student_ids" keys.
- All responses are JSON-formatted unless otherwise specified (e.g., DELETE returns empty body).
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import db
from app.models.lesson_model import Lesson
from app.schemas.schemas import LessonSchema
from app.models.student_model import Student
from app.models.quiz_model import Quiz
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
    lesson_data = data.get("lesson", {})
    student_ids = data.get("student_ids", [])

    lesson_schema = LessonSchema()
    lesson = lesson_schema.load(lesson_data, instance=lesson, partial=True)
    if student_ids:
        lesson.students = Student.query.filter(Student.id.in_(student_ids)).all()
    db.session.add(lesson)
    db.session.commit()
    return lesson_schema.dump(lesson), 201

@lessons_bp.route('/lessons/<int:id>', methods=['PUT'])
@jwt_required()
@response_wrapper
def update_lesson(id):
    lesson = Lesson.query.get_or_404(id)
    data = request.get_json()
    lesson_data = data.get("lesson", {})
    student_ids = data.get("student_ids", [])

    lesson_schema = LessonSchema()
    updated_lesson = lesson_schema.load(lesson_data, instance=lesson, partial=True)
    if student_ids:
        lesson.students = Student.query.filter(Student.id.in_(student_ids)).all()
    db.session.commit()
    return lesson_schema.dump(updated_lesson), 200

@lessons_bp.route('/lessons/<int:id>', methods=['DELETE'])
@jwt_required()
@response_wrapper
def delete_lesson(id):
    lesson = Lesson.query.get_or_404(id)
    db.session.delete(lesson)
    db.session.commit()
    return '', 204