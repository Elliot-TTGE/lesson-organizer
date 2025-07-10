from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import db
from app.models.student_status_history_model import StudentStatusHistory
from app.models.student_model import Student
from app.models.student_status_model import StudentStatus
from app.schemas.schemas import StudentStatusHistorySchema
from app.routes.utils import response_wrapper

student_status_history_bp = Blueprint('student_status_history', __name__)

@student_status_history_bp.route('/student-status-history', methods=['GET'])
@jwt_required()
@response_wrapper
def get_student_status_history():
    """
    GET /student-status-history

    Query Parameters:
    - id: int (optional) — Get a single history record by ID.
    - student_id: int (optional) — Filter by student ID.
    - status_id: int (optional) — Filter by status ID.
    - start_date: str (optional, ISO date) — Filter records after this date.
    - end_date: str (optional, ISO date) — Filter records before this date.
    - do_paginate: bool (optional, default=false) — Whether to return pagination data.
    - page: int (optional, default=1) — Pagination page number.
    - per_page: int (optional, default=20) — Pagination page size.

    Returns:
    - 200: JSON array of history records or single record.
    - 404: If record not found (when using id).
    """
    record_id = request.args.get('id', type=int)
    student_id = request.args.get('student_id', type=int)
    status_id = request.args.get('status_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    do_paginate = request.args.get('do_paginate', 'false').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Get single record by ID
    if record_id:
        record = StudentStatusHistory.query.get_or_404(record_id)
        schema = StudentStatusHistorySchema()
        return schema.dump(record), 200

    # Build query
    query = StudentStatusHistory.query

    # Filter by student ID
    if student_id:
        query = query.filter(StudentStatusHistory.student_id == student_id)

    # Filter by status ID
    if status_id:
        query = query.filter(StudentStatusHistory.status_id == status_id)

    # Filter by date range
    if start_date:
        try:
            from datetime import datetime
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(StudentStatusHistory.changed_at >= start_dt)
        except ValueError:
            return {"message": "Invalid start_date format. Use ISO format."}, 400

    if end_date:
        try:
            from datetime import datetime
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(StudentStatusHistory.changed_at <= end_dt)
        except ValueError:
            return {"message": "Invalid end_date format. Use ISO format."}, 400

    # Order by changed_at descending (most recent first)
    query = query.order_by(StudentStatusHistory.changed_at.desc())

    schema = StudentStatusHistorySchema(many=True)
    
    if do_paginate:
        # Paginate and return with pagination metadata
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        records = paginated.items
        
        return {
            "student_status_history": schema.dump(records),
            "pagination": {
                "page": paginated.page,
                "pages": paginated.pages,
                "per_page": paginated.per_page,
                "total": paginated.total
            }
        }
    else:
        # Return all results without pagination
        records = query.all()
        return {"student_status_history": schema.dump(records)}

@student_status_history_bp.route('/student-status-history', methods=['POST'])
@jwt_required()
@response_wrapper
def create_student_status_history():
    """
    POST /student-status-history

    Description:
    Create a new student status history record.

    Request JSON Body:
    {
        "student_status_history": {
            "student_id": int,       # required
            "status_id": int,        # required
            "changed_at": str        # required, ISO date string
        }
    }

    Returns:
    - 201: JSON object of the created record (marshmallow schema)
    - 400: If validation fails or required fields are missing
    - 404: If student or status not found
    """
    data = request.get_json()
    if not data or 'student_status_history' not in data:
        return {"message": "Student status history data is required in 'student_status_history' key"}, 400
    
    history_data = data['student_status_history']

    # Validate required fields
    if not history_data.get("student_id"):
        return {"message": "student_id field is required"}, 400
    
    if not history_data.get("status_id"):
        return {"message": "status_id field is required"}, 400
    
    if not history_data.get("changed_at"):
        return {"message": "changed_at field is required"}, 400

    # Verify student exists
    student_id = history_data.get("student_id")
    student = Student.query.get(student_id)
    if not student:
        return {"message": "Invalid student_id"}, 404

    # Verify status exists
    status_id = history_data.get("status_id")
    status = StudentStatus.query.get(status_id)
    if not status:
        return {"message": "Invalid status_id"}, 404

    schema = StudentStatusHistorySchema()
    try:
        record = schema.load(history_data)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.add(record)
    db.session.commit()
    return schema.dump(record), 201

@student_status_history_bp.route('/student-status-history/<int:id>', methods=['PUT'])
@jwt_required()
@response_wrapper
def update_student_status_history(id):
    """
    PUT /student-status-history/<record_id>

    Description:
    Update a single student status history record by ID.

    Path Parameters:
    - record_id: int — The ID of the record to update.

    Request JSON Body:
    {
        "student_status_history": {
            "student_id": int,       # optional
            "status_id": int,        # optional
            "changed_at": str        # optional, ISO date string
        }
    }

    Returns:
    - 200: JSON object of the updated record (marshmallow schema)
    - 400: If validation fails
    - 404: If record, student, or status not found
    """
    record = StudentStatusHistory.query.get_or_404(id)
    data = request.get_json()
    if not data or 'student_status_history' not in data:
        return {"message": "Student status history data is required in 'student_status_history' key"}, 400
    
    history_data = data['student_status_history']

    # If student_id is being updated, verify it exists
    if 'student_id' in history_data:
        student_id = history_data.get("student_id")
        student = Student.query.get(student_id)
        if not student:
            return {"message": "Invalid student_id"}, 404

    # If status_id is being updated, verify it exists
    if 'status_id' in history_data:
        status_id = history_data.get("status_id")
        status = StudentStatus.query.get(status_id)
        if not status:
            return {"message": "Invalid status_id"}, 404

    schema = StudentStatusHistorySchema(partial=True)
    try:
        updated_record = schema.load(history_data, instance=record, partial=True)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.commit()
    return schema.dump(updated_record), 200

@student_status_history_bp.route('/student-status-history/<int:id>', methods=['DELETE'])
@jwt_required()
@response_wrapper
def delete_student_status_history(id):
    """
    DELETE /student-status-history/<record_id>

    Description:
    Delete a single student status history record by ID.

    Path Parameters:
    - record_id: int — The ID of the record to delete.

    Returns:
    - 204: No content (successful deletion)
    - 404: If record not found
    """
    record = StudentStatusHistory.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return '', 204
