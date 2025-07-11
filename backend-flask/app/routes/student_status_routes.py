from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import db
from app.models.student_status_model import StudentStatus
from app.schemas.schemas import StudentStatusSchema
from app.routes.utils import response_wrapper

student_status_bp = Blueprint('student_status', __name__)

@student_status_bp.route('/student-statuses', methods=['GET'])
@jwt_required()
@response_wrapper
def get_student_statuses():
    """
    GET /student-statuses

    Query Parameters:
    - name: str (optional) — Filter statuses by name (partial match).

    Returns:
    - 200: JSON array of statuses.
    """
    name = request.args.get('name')

    # Build query
    query = StudentStatus.query

    # Filter by name (partial match)
    if name:
        query = query.filter(StudentStatus.name.ilike(f'%{name}%'))

    # Order by name for consistent ordering
    query = query.order_by(StudentStatus.name)

    statuses = query.all()
    schema = StudentStatusSchema(many=True)
    return schema.dump(statuses), 200

#@student_status_bp.route('/student-statuses', methods=['POST'])
@jwt_required()
@response_wrapper
def create_student_status():
    """
    POST /student-statuses

    Description:
    Create a new student status.

    Request JSON Body:
    {
        "student_status": {
            "name": str              # required
        }
    }

    Returns:
    - 201: JSON object of the created status (marshmallow schema)
    - 400: If validation fails or required fields are missing
    """
    data = request.get_json()
    if not data or 'student_status' not in data:
        return {"message": "Student status data is required in 'student_status' key"}, 400
    
    status_data = data['student_status']

    # Validate required fields
    if not status_data.get("name"):
        return {"message": "name field is required"}, 400

    schema = StudentStatusSchema()
    try:
        status = schema.load(status_data)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.add(status)
    db.session.commit()
    return schema.dump(status), 201

#@student_status_bp.route('/student-statuses/<int:id>', methods=['PUT'])
@jwt_required()
@response_wrapper
def update_student_status(id):
    """
    PUT /student-statuses/<status_id>

    Description:
    Update a single student status by ID.

    Path Parameters:
    - status_id: int — The ID of the status to update.

    Request JSON Body:
    {
        "student_status": {
            "name": str              # optional
        }
    }

    Returns:
    - 200: JSON object of the updated status (marshmallow schema)
    - 400: If validation fails
    - 404: If status not found
    """
    status = StudentStatus.query.get_or_404(id)
    data = request.get_json()
    if not data or 'student_status' not in data:
        return {"message": "Student status data is required in 'student_status' key"}, 400
    
    status_data = data['student_status']

    schema = StudentStatusSchema(partial=True)
    try:
        updated_status = schema.load(status_data, instance=status, partial=True)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.commit()
    return schema.dump(updated_status), 200

#@student_status_bp.route('/student-statuses/<int:id>', methods=['DELETE'])
@jwt_required()
@response_wrapper
def delete_student_status(id):
    """
    DELETE /student-statuses/<status_id>

    Description:
    Delete a single student status by ID. This will also delete all associated status history.

    Path Parameters:
    - status_id: int — The ID of the status to delete.

    Returns:
    - 204: No content (successful deletion)
    - 404: If status not found
    """
    status = StudentStatus.query.get_or_404(id)
    db.session.delete(status)
    db.session.commit()
    return '', 204

@student_status_bp.route('/student-statuses/<int:status_id>', methods=['GET'])
@jwt_required()
@response_wrapper
def get_student_status(status_id):
    """
    GET /student-statuses/<status_id>

    Description:
    Get a single student status by ID.

    Path Parameters:
    - status_id: int — The ID of the student status to retrieve.

    Returns:
    - 200: JSON object of the student status (marshmallow schema)
    - 404: If student status not found
    """
    status = StudentStatus.query.get_or_404(status_id)
    schema = StudentStatusSchema()
    return schema.dump(status)
