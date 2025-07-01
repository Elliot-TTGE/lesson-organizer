from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import db
from app.models.student_level_history_model import StudentLevelHistory
from app.models.student_model import Student
from app.models.level_model import Level
from app.schemas.schemas import StudentLevelHistorySchema
from app.routes.utils import response_wrapper

student_level_history_bp = Blueprint('student_level_history', __name__)

@student_level_history_bp.route('/student-level-history', methods=['GET'])
@jwt_required()
@response_wrapper
def get_student_level_history():
    """
    GET /student-level-history

    Query Parameters:
    - id: int (optional) — Get a single history record by ID.
    - student_id: int (optional) — Filter by student ID.
    - level_id: int (optional) — Filter by level ID.
    - start_date: str (optional, ISO date) — Filter records after this date.
    - end_date: str (optional, ISO date) — Filter records before this date.

    Returns:
    - 200: JSON array of history records or single record.
    - 404: If record not found (when using id).
    """
    record_id = request.args.get('id', type=int)
    student_id = request.args.get('student_id', type=int)
    level_id = request.args.get('level_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Get single record by ID
    if record_id:
        record = StudentLevelHistory.query.get_or_404(record_id)
        schema = StudentLevelHistorySchema()
        return schema.dump(record), 200

    # Build query
    query = StudentLevelHistory.query

    # Filter by student ID
    if student_id:
        query = query.filter(StudentLevelHistory.student_id == student_id)

    # Filter by level ID
    if level_id:
        query = query.filter(StudentLevelHistory.level_id == level_id)

    # Filter by start date range
    if start_date:
        try:
            from datetime import datetime
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(StudentLevelHistory.start_date >= start_dt)
        except ValueError:
            return {"message": "Invalid start_date format. Use ISO format."}, 400

    if end_date:
        try:
            from datetime import datetime
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(StudentLevelHistory.start_date <= end_dt)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use ISO format."}), 400

    # Order by start_date descending (most recent first)
    query = query.order_by(StudentLevelHistory.start_date.desc())

    records = query.all()
    schema = StudentLevelHistorySchema(many=True)
    return schema.dump(records), 200

@student_level_history_bp.route('/student-level-history', methods=['POST'])
@jwt_required()
@response_wrapper
def create_student_level_history():
    """
    POST /student-level-history

    Description:
    Create a new student level history record.

    Request JSON Body:
    {
        "student_level_history": {
            "student_id": int,       # required
            "level_id": int,         # required
            "start_date": str        # required, ISO date string
        }
    }

    Returns:
    - 201: JSON object of the created record (marshmallow schema)
    - 400: If validation fails or required fields are missing
    - 404: If student or level not found
    """
    data = request.get_json()
    if not data or 'student_level_history' not in data:
        return {"message": "Student level history data is required in 'student_level_history' key"}, 400
    
    student_level_history_data = data['student_level_history']

    # Validate required fields
    if not student_level_history_data.get("student_id"):
        return {"message": "student_id field is required"}, 400
    
    if not student_level_history_data.get("level_id"):
        return {"message": "level_id field is required"}, 400
    
    if not student_level_history_data.get("start_date"):
        return {"message": "start_date field is required"}, 400

    # Verify student exists
    student_id = student_level_history_data.get("student_id")
    student = Student.query.get(student_id)
    if not student:
        return {"message": "Invalid student_id"}, 404

    # Verify level exists
    level_id = student_level_history_data.get("level_id")
    level = Level.query.get(level_id)
    if not level:
        return {"message": "Invalid level_id"}, 404

    schema = StudentLevelHistorySchema()
    try:
        record = schema.load(student_level_history_data)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.add(record)
    db.session.commit()
    return schema.dump(record), 201

@student_level_history_bp.route('/student-level-history/<int:id>', methods=['PUT'])
@jwt_required()
@response_wrapper
def update_student_level_history(id):
    """
    PUT /student-level-history/<record_id>

    Description:
    Update a single student level history record by ID.

    Path Parameters:
    - record_id: int — The ID of the record to update.

    Request JSON Body:
    {
        "student_level_history": {
            "student_id": int,       # optional
            "level_id": int,         # optional
            "start_date": str        # optional, ISO date string
        }
    }

    Returns:
    - 200: JSON object of the updated record (marshmallow schema)
    - 400: If validation fails
    - 404: If record, student, or level not found
    """
    record = StudentLevelHistory.query.get_or_404(id)
    data = request.get_json()
    if not data or 'student_level_history' not in data:
        return {"message": "Student level history data is required in 'student_level_history' key"}, 400
    
    student_level_history_data = data['student_level_history']

    # If student_id is being updated, verify it exists
    if 'student_id' in student_level_history_data:
        student_id = student_level_history_data.get("student_id")
        student = Student.query.get(student_id)
        if not student:
            return {"message": "Invalid student_id"}, 404

    # If level_id is being updated, verify it exists
    if 'level_id' in student_level_history_data:
        level_id = student_level_history_data.get("level_id")
        level = Level.query.get(level_id)
        if not level:
            return {"message": "Invalid level_id"}, 404

    schema = StudentLevelHistorySchema(partial=True)
    try:
        updated_record = schema.load(student_level_history_data, instance=record, partial=True)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.commit()
    return schema.dump(updated_record), 200

@student_level_history_bp.route('/student-level-history/<int:id>', methods=['DELETE'])
@jwt_required()
@response_wrapper
def delete_student_level_history(id):
    """
    DELETE /student-level-history/<record_id>

    Description:
    Delete a single student level history record by ID.

    Path Parameters:
    - record_id: int — The ID of the record to delete.

    Returns:
    - 204: No Content (successful deletion)
    - 404: If record not found
    """
    record = StudentLevelHistory.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return '', 204