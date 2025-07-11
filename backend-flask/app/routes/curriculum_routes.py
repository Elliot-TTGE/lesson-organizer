from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import db
from app.models.curriculum_model import Curriculum
from app.schemas.schemas import CurriculumSchema
from app.routes.utils import response_wrapper

curriculum_bp = Blueprint('curriculum', __name__)

@curriculum_bp.route('/curriculums', methods=['GET'])
@jwt_required()
@response_wrapper
def get_curriculums():
    """
    GET /curriculums

    Query Parameters:
    - name: str (optional) — Filter curriculums by name (partial match).

    Returns:
    - 200: JSON array of curriculums.
    """
    name = request.args.get('name')

    # Build query
    query = Curriculum.query

    # Filter by name (partial match)
    if name:
        query = query.filter(Curriculum.name.ilike(f'%{name}%'))

    curriculums = query.all()
    curriculum_schema = CurriculumSchema(many=True)
    return curriculum_schema.dump(curriculums), 200

#@curriculum_bp.route('/curriculums', methods=['POST'])
@jwt_required()
@response_wrapper
def create_curriculum():
    """
    POST /curriculums

    Description:
    Create a new curriculum.

    Request JSON Body:
    {
        "curriculum": {
            "name": str              # required
        }
    }

    Returns:
    - 201: JSON object of the created curriculum (marshmallow schema)
    - 400: If validation fails or required fields are missing
    """
    data = request.get_json()
    if not data or 'curriculum' not in data:
        return {"message": "Curriculum data is required in 'curriculum' key"}, 400
    
    curriculum_data = data['curriculum']

    # Validate required fields
    if not curriculum_data.get("name"):
        return {"message": "name field is required"}, 400

    curriculum_schema = CurriculumSchema()
    try:
        curriculum = curriculum_schema.load(curriculum_data)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.add(curriculum)
    db.session.commit()
    return curriculum_schema.dump(curriculum), 201

#@curriculum_bp.route('/curriculums/<int:id>', methods=['PUT'])
@jwt_required()
@response_wrapper
def update_curriculum(id):
    """
    PUT /curriculums/<curriculum_id>

    Description:
    Update a single curriculum by ID.

    Path Parameters:
    - curriculum_id: int — The ID of the curriculum to update.

    Request JSON Body:
    {
        "curriculum": {
            "name": str              # optional
        }
    }

    Returns:
    - 200: JSON object of the updated curriculum (marshmallow schema)
    - 400: If validation fails
    - 404: If curriculum not found
    """
    curriculum = Curriculum.query.get_or_404(id)
    data = request.get_json()
    if not data or 'curriculum' not in data:
        return {"message": "Curriculum data is required in 'curriculum' key"}, 400
    
    curriculum_data = data['curriculum']

    curriculum_schema = CurriculumSchema(partial=True)
    try:
        updated_curriculum = curriculum_schema.load(curriculum_data, instance=curriculum, partial=True)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.commit()
    return curriculum_schema.dump(updated_curriculum), 200

#@curriculum_bp.route('/curriculums/<int:id>', methods=['DELETE'])
@jwt_required()
@response_wrapper
def delete_curriculum(id):
    """
    DELETE /curriculums/<curriculum_id>

    Description:
    Delete a single curriculum by ID. This will also delete all associated levels.

    Path Parameters:
    - curriculum_id: int — The ID of the curriculum to delete.

    Returns:
    - 204: No content (successful deletion)
    - 404: If curriculum not found
    """
    curriculum = Curriculum.query.get_or_404(id)
    db.session.delete(curriculum)
    db.session.commit()
    return '', 204

@curriculum_bp.route('/curriculums/<int:curriculum_id>', methods=['GET'])
@jwt_required()
@response_wrapper
def get_curriculum(curriculum_id):
    """
    GET /curriculums/<curriculum_id>

    Description:
    Get a single curriculum by ID.

    Path Parameters:
    - curriculum_id: int — The ID of the curriculum to retrieve.

    Returns:
    - 200: JSON object of the curriculum (marshmallow schema)
    - 404: If curriculum not found
    """
    curriculum = Curriculum.query.get_or_404(curriculum_id)
    curriculum_schema = CurriculumSchema()
    return curriculum_schema.dump(curriculum)