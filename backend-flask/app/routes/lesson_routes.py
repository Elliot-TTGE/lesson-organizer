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
    """
    GET /lessons

    Query Parameters:
    - id: int (optional) — Get a single lesson by ID.
    - student_id: int (optional) — Filter lessons by student ID.
    - start: str (optional, ISO date) — Filter lessons after this date.
    - end: str (optional, ISO date) — Filter lessons before this date.
    - group: str (optional, "true"/"false") — Filter group lessons.
    - page: int (optional, default=1) — Pagination page number.
    - per_page: int (optional, default=20) — Pagination page size.

    Returns:
    - 200: JSON object with lessons, pagination info.
    - 404: If lesson not found (when using id).
    """
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
    """
    POST /lessons

    Description:
    Create a new lesson. Only one lesson object should be sent per request.

    Request JSON Body:
    {
        "datetime": str,         # required, ISO date string
        "plan": str,             # optional
        "concepts": str,         # optional
        "notes": str             # optional
    }

    Returns:
    - 201: JSON object of the created lesson (marshmallow schema)
    - 400: If validation fails or required fields are missing
    """
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
    """
    PUT /lessons/<lesson_id>

    Description:
    Update a single lesson by ID.

    Path Parameters:
    - lesson_id: int — The ID of the lesson to update.

    Request JSON Body:
    {
        "datetime": str,         # optional, ISO date string
        "plan": str,             # optional
        "concepts": str,         # optional
        "notes": str             # optional
    }

    Returns:
    - 200: JSON object of the updated lesson (marshmallow schema)
    - 400: If validation fails or required fields are missing
    - 404: If lesson not found
    """
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
    """
    DELETE /lessons/<lesson_id>

    Description:
    Delete a single lesson by ID.

    Path Parameters:
    - lesson_id: int — The ID of the lesson to delete.

    Returns:
    - 204: No content if deletion is successful
    - 404: If lesson not found
    """
    lesson = Lesson.query.get_or_404(id)
    db.session.delete(lesson)
    db.session.commit()
    return '', 204