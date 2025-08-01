from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import db
from app.models.level_model import Level
from app.models.curriculum_model import Curriculum
from app.schemas.schemas import LevelSchema
from app.routes.utils import response_wrapper

level_bp = Blueprint('level', __name__)

@level_bp.route('/levels', methods=['GET'])
@jwt_required()
@response_wrapper
def get_levels():
    """
    GET /levels

    Query Parameters:
    - name: str (optional) — Filter levels by name (partial match).
    - curriculum_id: int (optional) — Filter levels by curriculum ID.

    Returns:
    - 200: JSON array of levels.
    """
    name = request.args.get('name')
    curriculum_id = request.args.get('curriculum_id', type=int)

    # Build query
    query = Level.query

    # Filter by curriculum ID
    if curriculum_id:
        query = query.filter(Level.curriculum_id == curriculum_id)

    # Filter by name (partial match)
    if name:
        query = query.filter(Level.name.ilike(f'%{name}%'))

    # Order by curriculum_id, then by name for consistent ordering
    query = query.order_by(Level.curriculum_id, Level.name)

    levels = query.all()
    level_schema = LevelSchema(many=True)
    return level_schema.dump(levels), 200

@level_bp.route('/levels', methods=['POST'])
@jwt_required()
@response_wrapper
def create_level():
    """
    POST /levels

    Description:
    Create a new level.

    Request JSON Body:
    {
        "level": {
            "name": str,             # required
            "curriculum_id": int     # required
        }
    }

    Returns:
    - 201: JSON object of the created level (marshmallow schema)
    - 400: If validation fails or required fields are missing
    - 404: If curriculum not found
    """
    data = request.get_json()
    if not data or 'level' not in data:
        return {"message": "Level data is required in 'level' key"}, 400
    
    level_data = data['level']

    # Validate required fields
    if not level_data.get("name"):
        return {"message": "name field is required"}, 400
    
    if not level_data.get("curriculum_id"):
        return {"message": "curriculum_id field is required"}, 400

    # Verify curriculum exists
    curriculum_id = level_data.get("curriculum_id")
    curriculum = Curriculum.query.get(curriculum_id)
    if not curriculum:
        return {"message": "Invalid curriculum_id"}, 404

    level_schema = LevelSchema()
    try:
        level = level_schema.load(level_data)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.add(level)
    db.session.commit()
    return level_schema.dump(level), 201

@level_bp.route('/levels/<int:id>', methods=['PUT'])
@jwt_required()
@response_wrapper
def update_level(id):
    """
    PUT /levels/<level_id>

    Description:
    Update a single level by ID.

    Path Parameters:
    - level_id: int — The ID of the level to update.

    Request JSON Body:
    {
        "level": {
            "name": str,             # optional
            "curriculum_id": int     # optional
        }
    }

    Returns:
    - 200: JSON object of the updated level (marshmallow schema)
    - 400: If validation fails
    - 404: If level or curriculum not found
    """
    level = Level.query.get_or_404(id)
    data = request.get_json()
    if not data or 'level' not in data:
        return {"message": "Level data is required in 'level' key"}, 400
    
    level_data = data['level']

    # If curriculum_id is being updated, verify it exists
    if 'curriculum_id' in level_data:
        curriculum_id = level_data.get("curriculum_id")
        curriculum = Curriculum.query.get(curriculum_id)
        if not curriculum:
            return {"message": "Invalid curriculum_id"}, 404

    level_schema = LevelSchema(partial=True)
    try:
        updated_level = level_schema.load(level_data, instance=level, partial=True)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.commit()
    return level_schema.dump(updated_level), 200

@level_bp.route('/levels/<int:id>', methods=['DELETE'])
@jwt_required()
@response_wrapper
def delete_level(id):
    """
    DELETE /levels/<level_id>

    Description:
    Delete a single level by ID. This will also delete all associated units and student level history.

    Path Parameters:
    - level_id: int — The ID of the level to delete.

    Returns:
    - 204: No content (successful deletion)
    - 404: If level not found
    """
    level = Level.query.get_or_404(id)
    db.session.delete(level)
    db.session.commit()
    return '', 204

@level_bp.route('/levels/<int:level_id>', methods=['GET'])
@jwt_required()
@response_wrapper
def get_level(level_id):
    """
    GET /levels/<level_id>

    Description:
    Get a single level by ID.

    Path Parameters:
    - level_id: int — The ID of the level to retrieve.

    Returns:
    - 200: JSON object of the level (marshmallow schema)
    - 404: If level not found
    """
    level = Level.query.get_or_404(level_id)
    level_schema = LevelSchema()
    return level_schema.dump(level)