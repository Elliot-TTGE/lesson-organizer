from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import db
from app.models.student_model import Student
from app.models.student_status_history_model import StudentStatusHistory
from app.models.student_level_history_model import StudentLevelHistory
from app.models.student_status_model import StudentStatus
from app.models.level_model import Level
from app.models.lesson_model import Lesson
from app.schemas.schemas import StudentSchema
from sqlalchemy import func, and_, or_
from app.routes.utils import response_wrapper

student_bp = Blueprint('student', __name__)

@student_bp.route('/students', methods=['GET'])
@jwt_required()
@response_wrapper
def get_students():
    """
    GET /students

    Query Parameters:
    - status: str (optional) — Filter by current status (from StudentStatusHistory).
    - level: str (optional) — Filter by current level (from StudentLevelHistory).
    - search: str (optional) — Search by first name or last name (case-insensitive).
    - lesson_start: str (optional, ISO date) — Filter students who had lessons after this date.
    - lesson_end: str (optional, ISO date) — Filter students who had lessons before this date.
    - is_in_group: str (optional, "true"/"false") — Filter students who had group lessons (multiple students in one lesson).
    - started_after: str (optional, ISO date) — Filter students who started after this date.
    - classes_per_week: int (optional) — Filter by number of classes per week.
    - do_paginate: bool (optional, default=false) — Whether to return pagination data.
    - page: int (optional, default=1) — Pagination page number.
    - per_page: int (optional, default=20) — Pagination page size.

    Returns:
    - 200: JSON object with students, pagination info.
    """
    status = request.args.get("status")
    level = request.args.get("level")
    search = request.args.get("search")                           # Search by name
    lesson_start = request.args.get("lesson_start")              # ISO date string
    lesson_end = request.args.get("lesson_end")                  # ISO date string
    is_in_group = request.args.get("is_in_group")                # "true" or "false"
    started_after = request.args.get("started_after")            # ISO date string
    classes_per_week = request.args.get("classes_per_week")
    do_paginate = request.args.get('do_paginate', 'false').lower() == 'true'
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    query = Student.query

    # Filter by name search (first name or last name)
    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(
            or_(
                func.lower(Student.first_name).like(search_term),
                func.lower(Student.last_name).like(search_term)
            )
        )

    # Filter by current status (latest StudentStatusHistory)
    if status:
        subq = db.session.query(
            StudentStatusHistory.student_id,
            func.max(StudentStatusHistory.changed_at).label("max_changed_at")
        ).group_by(StudentStatusHistory.student_id).subquery()

        query = query.join(
            subq, Student.id == subq.c.student_id
        ).join(
            StudentStatusHistory,
            and_(
                StudentStatusHistory.student_id == subq.c.student_id,
                StudentStatusHistory.changed_at == subq.c.max_changed_at
            )
        ).join(
            StudentStatus, StudentStatusHistory.status_id == StudentStatus.id
        ).filter(StudentStatus.name == status)

    # Filter by current level (latest StudentLevelHistory)
    if level:
        subq = db.session.query(
            StudentLevelHistory.student_id,
            func.max(StudentLevelHistory.start_date).label("max_start_date")
        ).group_by(StudentLevelHistory.student_id).subquery()

        query = query.join(
            subq, Student.id == subq.c.student_id
        ).join(
            StudentLevelHistory,
            and_(
                StudentLevelHistory.student_id == subq.c.student_id,
                StudentLevelHistory.start_date == subq.c.max_start_date
            )
        ).join(
            Level, StudentLevelHistory.level_id == Level.id
        ).filter(Level.name == level)

    # Filter by students who had lessons in a time range
    if lesson_start or lesson_end:
        query = query.join(Student.lessons)
        if lesson_start:
            query = query.filter(Lesson.datetime >= lesson_start)
        if lesson_end:
            query = query.filter(Lesson.datetime <= lesson_end)

    # Filter by group lessons (lessons with >1 student)
    if is_in_group is not None:
        query = query.join(Student.lessons)
        group_subq = db.session.query(
            Lesson.id
        ).join(Lesson.students).group_by(Lesson.id).having(
            func.count(Student.id) > 1 if is_in_group == "true" else func.count(Student.id) == 1
        ).subquery()
        query = query.filter(Lesson.id.in_(group_subq))

    # Filter by students who started after a given date
    if started_after:
        query = query.filter(Student.date_started >= started_after)

    # Filter by classes per week
    if classes_per_week:
        query = query.filter(Student.classes_per_week == int(classes_per_week))

    schema = StudentSchema(many=True)
    
    if do_paginate:
        # Paginate and return with pagination metadata
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        students = paginated.items
        
        return {
            "students": schema.dump(students),
            "pagination": {
                "page": paginated.page,
                "pages": paginated.pages,
                "per_page": paginated.per_page,
                "total": paginated.total
            }
        }
    else:
        # Return all results without pagination
        students = query.all()
        return {"students": schema.dump(students)}

@student_bp.route('/students', methods=['POST'])
@jwt_required()
@response_wrapper
def create_student():
    """
    POST /students

    Description:
    Create a new student. Only one student object should be sent per request.

    Request JSON Body:
    {
        "student": {
            "first_name": str,           # required
            "last_name": str,            # optional
            "date_started": str,         # optional, ISO date string
            "classes_per_week": int,     # optional
            "notes_general": str,        # optional
            "notes_strengths": str,      # optional
            "notes_weaknesses": str,     # optional
            "notes_future": str          # optional
        }
    }

    Returns:
    - 201: JSON object of the created student (marshmallow schema)
    - 400: If validation fails or required fields are missing
    """
    data = request.get_json()
    if not data or 'student' not in data:
        return {"message": "Student data is required in 'student' key"}, 400
    
    student_data = data['student']
    schema = StudentSchema()
    try:
        student = schema.load(student_data)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.add(student)
    db.session.commit()
    return schema.dump(student), 201

@student_bp.route('/students/<int:student_id>', methods=['PUT'])
@jwt_required()
@response_wrapper
def update_student(student_id):
    """
    PUT /students/<student_id>

    Description:
    Update a single student by ID. Only one student object should be sent per request.

    Path Parameters:
    - student_id: int — The ID of the student to update.

    Request JSON Body:
    {
        "student": {
            "first_name": str,           # optional
            "last_name": str,            # optional
            "date_started": str,         # optional, ISO date string
            "classes_per_week": int,     # optional
            "notes_general": str,        # optional
            "notes_strengths": str,      # optional
            "notes_weaknesses": str,     # optional
            "notes_future": str          # optional
        }
    }

    Returns:
    - 200: JSON object of the updated student (marshmallow schema)
    - 400: If validation fails or required fields are missing
    - 404: If student not found
    """
    student = Student.query.get(student_id)
    if not student:
        return {"message": "Student not found"}, 404

    data = request.get_json()
    if not data or 'student' not in data:
        return {"message": "Student data is required in 'student' key"}, 400
    
    student_data = data['student']
    schema = StudentSchema(partial=True)
    try:
        updated_student = schema.load(student_data, instance=student, partial=True)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.commit()
    return schema.dump(updated_student), 200

@student_bp.route('/students/<int:student_id>', methods=['DELETE'])
@jwt_required()
@response_wrapper
def delete_student(student_id):
    """
    DELETE /students/<student_id>

    Description:
    Delete a single student by ID.

    Path Parameters:
    - student_id: int — The ID of the student to delete.

    Returns:
    - 204: No content if deletion is successful
    - 404: If student not found
    """
    student = Student.query.get(student_id)
    if not student:
        return {"message": "Student not found"}, 404

    db.session.delete(student)
    db.session.commit()
    return {}, 204

@student_bp.route('/students/<int:student_id>', methods=['GET'])
@jwt_required()
@response_wrapper
def get_student(student_id):
    """
    GET /students/<student_id>

    Description:
    Get a single student by ID.

    Path Parameters:
    - student_id: int — The ID of the student to retrieve.

    Returns:
    - 200: JSON object of the student (marshmallow schema)
    - 404: If student not found
    """
    student = Student.query.get(student_id)
    if not student:
        return {"message": "Student not found"}, 404
    
    schema = StudentSchema()
    return schema.dump(student)