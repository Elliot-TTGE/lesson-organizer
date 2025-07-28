from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import db
from app.models.lesson_model import Lesson
from app.schemas.schemas import LessonSchema
from app.models.student_model import Student
from app.models.quiz_model import Quiz
from app.routes.utils import response_wrapper
from datetime import datetime, timezone, timedelta
from sqlalchemy import func

lesson_bp = Blueprint('lessons', __name__)


@lesson_bp.route('/lessons', methods=['GET'])
@jwt_required()
@response_wrapper
def get_lessons():
    """
    GET /lessons

    Query Parameters:
    - student_id: int (optional) — Filter lessons by student ID.
    - start: str (optional, ISO date) — Filter lessons after this date (defaults to today if range_length is used).
    - end: str (optional, ISO date) — Filter lessons before this date (takes priority over range_length).
    - range_length: int (optional, default=7) — Number of days from start date to include (ignored if end is provided).
    - group: str (optional, "true"/"false") — Filter group lessons.
    - do_paginate: bool (optional, default=false) — Whether to return pagination data.
    - page: int (optional, default=1) — Pagination page number.
    - per_page: int (optional, default=20) — Pagination page size.

    Returns:
    - 200: JSON object with lessons, pagination info.
    
    Note: If no start date is provided but range_length is used, start defaults to today.
    """
    student_id = request.args.get('student_id', type=int)
    start = request.args.get('start')
    end = request.args.get('end')
    range_length = request.args.get('range_length', type=int)
    group = request.args.get('group')
    do_paginate = request.args.get('do_paginate', 'false').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Build query
    query = Lesson.query

    # Apply filters
    if student_id:
        query = query.join(Lesson.students).filter(Student.id == student_id)
    
    # Handle date filtering
    range_length_provided = request.args.get('range_length') is not None
    if start or end or range_length_provided:
        # Determine start date
        if start:
            try:
                start_date = datetime.fromisoformat(start)
            except ValueError:
                return {"message": "Invalid start date format. Use ISO format (YYYY-MM-DD)."}, 400
        else:
            # Default to today if using range_length without explicit start
            start_date = datetime.now(timezone.utc)
        
        query = query.filter(Lesson.datetime >= start_date)
        
        # Determine end date - end parameter takes priority over range_length
        if end:
            try:
                end_date = datetime.fromisoformat(end)
                query = query.filter(Lesson.datetime <= end_date)
            except ValueError:
                return {"message": "Invalid end date format. Use ISO format (YYYY-MM-DD)."}, 400
        else:
            # Use range_length from start_date, default to 7 if not provided
            days = range_length if range_length is not None else 7
            end_date = start_date + timedelta(days=days)
            query = query.filter(Lesson.datetime < end_date)

    if group is not None:
        if group.lower() == "true":
            # Group lessons (lessons with >1 student)
            group_subq = db.session.query(
                Lesson.id
            ).join(Lesson.students).group_by(Lesson.id).having(
                func.count(Student.id) > 1
            ).subquery()
            query = query.filter(Lesson.id.in_(group_subq))
        elif group.lower() == "false":
            # Individual lessons (lessons with 1 student)
            individual_subq = db.session.query(
                Lesson.id
            ).join(Lesson.students).group_by(Lesson.id).having(
                func.count(Student.id) == 1
            ).subquery()
            query = query.filter(Lesson.id.in_(individual_subq))

    # Order by datetime descending (most recent first)
    query = query.order_by(Lesson.datetime.desc())

    schema = LessonSchema(many=True)
    
    if do_paginate:
        # Paginate and return with pagination metadata
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        lessons = paginated.items
        
        return {
            "lessons": schema.dump(lessons),
            "pagination": {
                "page": paginated.page,
                "pages": paginated.pages,
                "per_page": paginated.per_page,
                "total": paginated.total
            }
        }
    else:
        # Return all results without pagination
        lessons = query.all()
        return {"lessons": schema.dump(lessons)}

@lesson_bp.route('/lessons', methods=['POST'])
@jwt_required()
@response_wrapper
def create_lesson():
    """
    POST /lessons

    Description:
    Create a new lesson. Only one lesson object should be sent per request.

    Request JSON Body:
    {
        "lesson": {
            "datetime": str,         # required, ISO date string
            "plan": str,             # optional
            "concepts": str,         # optional
            "notes": str             # optional
        },
        "student_ids": [int]         # optional, array of student IDs
    }

    Returns:
    - 201: JSON object of the created lesson (marshmallow schema)
    - 400: If validation fails or required fields are missing
    """
    data = request.get_json()
    lesson_data = data.get("lesson", {})
    student_ids = data.get("student_ids", [])

    lesson_schema = LessonSchema()
    lesson = lesson_schema.load(lesson_data, partial=True)
    if student_ids:
        lesson.students = Student.query.filter(Student.id.in_(student_ids)).all()
    db.session.add(lesson)
    db.session.commit()
    return lesson_schema.dump(lesson), 201

@lesson_bp.route('/lessons/<int:id>', methods=['PUT'])
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
        "lesson": {
            "datetime": str,         # required, ISO date string
            "plan": str,             # optional
            "concepts": str,         # optional
            "notes": str             # optional
        },
        "student_ids": [int]         # optional, array of student IDs
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

@lesson_bp.route('/lessons/<int:id>', methods=['DELETE'])
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

@lesson_bp.route('/lessons/<int:lesson_id>', methods=['GET'])
@jwt_required()
@response_wrapper
def get_lesson(lesson_id):
    """
    GET /lessons/<lesson_id>

    Description:
    Get a single lesson by ID.

    Path Parameters:
    - lesson_id: int — The ID of the lesson to retrieve.

    Returns:
    - 200: JSON object of the lesson (marshmallow schema)
    - 404: If lesson not found
    """
    lesson = Lesson.query.get_or_404(lesson_id)
    schema = LessonSchema()
    return schema.dump(lesson)