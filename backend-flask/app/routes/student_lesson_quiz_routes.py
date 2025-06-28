from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import db
from app.models.student_lesson_quiz_model import StudentLessonQuiz
from app.models.student_model import Student
from app.models.lesson_model import Lesson
from app.models.quiz_model import Quiz
from app.schemas.schemas import StudentLessonQuizSchema
from app.routes.utils import response_wrapper

student_lesson_quiz_bp = Blueprint('student_lesson_quiz', __name__)

@student_lesson_quiz_bp.route('/student-lesson-quizzes', methods=['GET'])
@jwt_required()
@response_wrapper
def get_student_lesson_quizzes():
    """
    GET /student-lesson-quizzes

    Query Parameters:
    - id: int (optional) — Get a single record by ID.
    - student_id: int (optional) — Filter by student ID.
    - lesson_id: int (optional) — Filter by lesson ID.
    - quiz_id: int (optional) — Filter by quiz ID.
    - page: int (optional, default=1) — Pagination page number.
    - per_page: int (optional, default=20) — Pagination page size.

    Returns:
    - 200: JSON object with records array and pagination info.
    - 404: If record not found (when using id).
    """
    record_id = request.args.get('id', type=int)
    student_id = request.args.get('student_id', type=int)
    lesson_id = request.args.get('lesson_id', type=int)
    quiz_id = request.args.get('quiz_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Get single record by ID
    if record_id:
        record = StudentLessonQuiz.query.get_or_404(record_id)
        schema = StudentLessonQuizSchema()
        return schema.dump(record), 200

    # Build query
    query = StudentLessonQuiz.query

    # Apply filters
    if student_id:
        query = query.filter(StudentLessonQuiz.student_id == student_id)
    if lesson_id:
        query = query.filter(StudentLessonQuiz.lesson_id == lesson_id)
    if quiz_id:
        query = query.filter(StudentLessonQuiz.quiz_id == quiz_id)

    # Order by created_date descending (most recent first)
    query = query.order_by(StudentLessonQuiz.created_date.desc())

    # Paginate
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    records = paginated.items

    schema = StudentLessonQuizSchema(many=True)
    return {
        "student_lesson_quizzes": schema.dump(records),
        "total": paginated.total,
        "page": paginated.page,
        "per_page": paginated.per_page,
        "pages": paginated.pages
    }

@student_lesson_quiz_bp.route('/student-lesson-quizzes', methods=['POST'])
@jwt_required()
@response_wrapper
def create_student_lesson_quiz():
    """
    POST /student-lesson-quizzes

    Description:
    Create a new student lesson quiz record.

    Request JSON Body:
    {
        "student_lesson_quiz": {
            "student_id": int,       # required
            "lesson_id": int,        # required
            "quiz_id": int,          # optional
            "points": int,           # optional
            "notes": str             # optional
        }
    }

    Returns:
    - 201: JSON object of the created record (marshmallow schema)
    - 400: If validation fails or required fields are missing
    - 404: If student, lesson, or quiz not found
    """
    data = request.get_json()
    if not data or 'student_lesson_quiz' not in data:
        return {"message": "Student lesson quiz data is required in 'student_lesson_quiz' key"}, 400
    
    record_data = data['student_lesson_quiz']

    # Validate required fields
    if not record_data.get("student_id"):
        return {"message": "student_id field is required"}, 400
    
    if not record_data.get("lesson_id"):
        return {"message": "lesson_id field is required"}, 400

    # Verify student exists
    student_id = record_data.get("student_id")
    student = Student.query.get(student_id)
    if not student:
        return {"message": "Invalid student_id"}, 404

    # Verify lesson exists
    lesson_id = record_data.get("lesson_id")
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return {"message": "Invalid lesson_id"}, 404

    # Verify quiz exists (if provided)
    quiz_id = record_data.get("quiz_id")
    if quiz_id:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {"message": "Invalid quiz_id"}, 404

    schema = StudentLessonQuizSchema()
    try:
        record = schema.load(record_data)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.add(record)
    db.session.commit()
    return schema.dump(record), 201

@student_lesson_quiz_bp.route('/student-lesson-quizzes/<int:id>', methods=['PUT'])
@jwt_required()
@response_wrapper
def update_student_lesson_quiz(id):
    """
    PUT /student-lesson-quizzes/<record_id>

    Description:
    Update a single student lesson quiz record by ID.

    Path Parameters:
    - record_id: int — The ID of the record to update.

    Request JSON Body:
    {
        "student_lesson_quiz": {
            "student_id": int,       # optional
            "lesson_id": int,        # optional
            "quiz_id": int,          # optional
            "points": int,           # optional
            "notes": str             # optional
        }
    }

    Returns:
    - 200: JSON object of the updated record (marshmallow schema)
    - 400: If validation fails
    - 404: If record, student, lesson, or quiz not found
    """
    record = StudentLessonQuiz.query.get_or_404(id)
    data = request.get_json()
    if not data or 'student_lesson_quiz' not in data:
        return {"message": "Student lesson quiz data is required in 'student_lesson_quiz' key"}, 400
    
    record_data = data['student_lesson_quiz']

    # Verify references if being updated
    if 'student_id' in record_data:
        student_id = record_data.get("student_id")
        student = Student.query.get(student_id)
        if not student:
            return {"message": "Invalid student_id"}, 404

    if 'lesson_id' in record_data:
        lesson_id = record_data.get("lesson_id")
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return {"message": "Invalid lesson_id"}, 404

    if 'quiz_id' in record_data and record_data.get("quiz_id"):
        quiz_id = record_data.get("quiz_id")
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {"message": "Invalid quiz_id"}, 404

    schema = StudentLessonQuizSchema(partial=True)
    try:
        updated_record = schema.load(record_data, instance=record, partial=True)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.commit()
    return schema.dump(updated_record), 200

@student_lesson_quiz_bp.route('/student-lesson-quizzes/<int:id>', methods=['DELETE'])
@jwt_required()
@response_wrapper
def delete_student_lesson_quiz(id):
    """
    DELETE /student-lesson-quizzes/<record_id>

    Description:
    Delete a single student lesson quiz record by ID.

    Path Parameters:
    - record_id: int — The ID of the record to delete.

    Returns:
    - 204: No content (successful deletion)
    - 404: If record not found
    """
    record = StudentLessonQuiz.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return '', 204
