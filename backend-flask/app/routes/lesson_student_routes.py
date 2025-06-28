from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import db
from app.models.lesson_student_model import LessonStudent
from app.models.lesson_model import Lesson
from app.models.student_model import Student
from app.schemas.schemas import LessonStudentSchema
from app.routes.utils import response_wrapper

lesson_student_bp = Blueprint('lesson_student', __name__)

@lesson_student_bp.route('/lesson-students', methods=['GET'])
@jwt_required()
@response_wrapper
def get_lesson_students():
    """
    GET /lesson-students

    Description:
    Get lesson-student associations with optional filtering.

    Query Parameters:
    - lesson_id: int (optional) — Filter by lesson ID.
    - student_id: int (optional) — Filter by student ID.
    - page: int (optional, default=1) — Pagination page number.
    - per_page: int (optional, default=20) — Pagination page size.

    Returns:
    - 200: JSON object with lesson-students array and pagination info.
    """
    lesson_id = request.args.get("lesson_id", type=int)
    student_id = request.args.get("student_id", type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = LessonStudent.query
    
    if lesson_id:
        query = query.filter_by(lesson_id=lesson_id)
    if student_id:
        query = query.filter_by(student_id=student_id)
    
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    lesson_students = paginated.items
    
    schema = LessonStudentSchema(many=True)
    return {
        "lesson_students": schema.dump(lesson_students),
        "total": paginated.total,
        "page": paginated.page,
        "per_page": paginated.per_page,
        "pages": paginated.pages
    }

@lesson_student_bp.route('/lesson-students', methods=['POST'])
@jwt_required()
@response_wrapper
def create_lesson_student():
    """
    POST /lesson-students

    Description:
    Create a new lesson-student association.

    Request JSON Body:
    {
        "lesson_student": {
            "lesson_id": int,        # required
            "student_id": int        # required
        }
    }

    Returns:
    - 201: JSON object of the created lesson-student association
    - 400: If validation fails or required fields are missing
    - 404: If lesson or student not found
    - 409: If association already exists
    """
    data = request.get_json()
    if not data or 'lesson_student' not in data:
        return {"message": "Lesson-student data is required in 'lesson_student' key"}, 400
    
    lesson_student_data = data['lesson_student']
    lesson_id = lesson_student_data.get("lesson_id")
    student_id = lesson_student_data.get("student_id")
    
    if not lesson_id or not student_id:
        return {"message": "lesson_id and student_id are required"}, 400

    # Check if lesson and student exist
    lesson = Lesson.query.get(lesson_id)
    student = Student.query.get(student_id)
    if not lesson or not student:
        return {"message": "Invalid lesson_id or student_id"}, 404

    # Prevent duplicate entries
    existing = LessonStudent.query.filter_by(lesson_id=lesson_id, student_id=student_id).first()
    if existing:
        return {"message": "This student is already assigned to the lesson"}, 409

    schema = LessonStudentSchema()
    try:
        lesson_student = schema.load(lesson_student_data)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.add(lesson_student)
    db.session.commit()
    return schema.dump(lesson_student), 201

@lesson_student_bp.route('/lesson-students/<int:lesson_student_id>', methods=['PUT'])
@jwt_required()
@response_wrapper
def update_lesson_student(lesson_student_id):
    """
    PUT /lesson-students/<lesson_student_id>

    Description:
    Update a lesson-student association by ID.

    Path Parameters:
    - lesson_student_id: int — The ID of the lesson-student association to update.

    Request JSON Body:
    {
        "lesson_student": {
            "lesson_id": int,        # optional
            "student_id": int        # optional
        }
    }

    Returns:
    - 200: JSON object of the updated lesson-student association
    - 400: If validation fails
    - 404: If lesson-student association not found
    - 409: If updated association would create a duplicate
    """
    lesson_student = LessonStudent.query.get(lesson_student_id)
    if not lesson_student:
        return {"message": "Lesson-student association not found"}, 404

    data = request.get_json()
    if not data or 'lesson_student' not in data:
        return {"message": "Lesson-student data is required in 'lesson_student' key"}, 400
    
    lesson_student_data = data['lesson_student']
    
    # Check for duplicate if lesson_id or student_id is being changed
    new_lesson_id = lesson_student_data.get("lesson_id", lesson_student.lesson_id)
    new_student_id = lesson_student_data.get("student_id", lesson_student.student_id)
    
    if new_lesson_id != lesson_student.lesson_id or new_student_id != lesson_student.student_id:
        existing = LessonStudent.query.filter_by(
            lesson_id=new_lesson_id, 
            student_id=new_student_id
        ).filter(LessonStudent.id != lesson_student_id).first()
        
        if existing:
            return {"message": "This student is already assigned to the lesson"}, 409

    schema = LessonStudentSchema(partial=True)
    try:
        updated_lesson_student = schema.load(lesson_student_data, instance=lesson_student, partial=True)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.commit()
    return schema.dump(updated_lesson_student), 200

@lesson_student_bp.route('/lesson-students/<int:lesson_student_id>', methods=['DELETE'])
@jwt_required()
@response_wrapper
def delete_lesson_student(lesson_student_id):
    """
    DELETE /lesson-students/<lesson_student_id>

    Description:
    Delete a lesson-student association by ID.

    Path Parameters:
    - lesson_student_id: int — The ID of the lesson-student association to delete.

    Returns:
    - 204: No content if deletion is successful
    - 404: If lesson-student association not found
    """
    lesson_student = LessonStudent.query.get(lesson_student_id)
    if not lesson_student:
        return {"message": "Lesson-student association not found"}, 404
    
    db.session.delete(lesson_student)
    db.session.commit()
    return '', 204