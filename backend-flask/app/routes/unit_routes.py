from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import db
from app.models.unit_model import Unit
from app.models.level_model import Level
from app.schemas.schemas import UnitSchema
from app.routes.utils import response_wrapper

unit_bp = Blueprint('unit', __name__)

@unit_bp.route('/units', methods=['GET'])
@jwt_required()
@response_wrapper
def get_units():
    """
    GET /units

    Query Parameters:
    - name: str (optional) — Filter units by name (partial match).
    - level_id: int (optional) — Filter units by level ID.

    Returns:
    - 200: JSON array of units.
    """
    name = request.args.get('name')
    level_id = request.args.get('level_id', type=int)

    # Build query
    query = Unit.query

    # Filter by level ID
    if level_id:
        query = query.filter(Unit.level_id == level_id)

    # Filter by name (partial match)
    if name:
        query = query.filter(Unit.name.ilike(f'%{name}%'))

    # Order by level_id, then by name for consistent ordering
    query = query.order_by(Unit.level_id, Unit.name)

    units = query.all()
    unit_schema = UnitSchema(many=True)
    return unit_schema.dump(units), 200

@unit_bp.route('/units', methods=['POST'])
@jwt_required()
@response_wrapper
def create_unit():
    """
    POST /units

    Description:
    Create a new unit.

    Request JSON Body:
    {
        "unit": {
            "name": str,             # required
            "level_id": int          # required
        }
    }

    Returns:
    - 201: JSON object of the created unit (marshmallow schema)
    - 400: If validation fails or required fields are missing
    - 404: If level not found
    """
    data = request.get_json()
    if not data or 'unit' not in data:
        return {"message": "Unit data is required in 'unit' key"}, 400
    
    unit_data = data['unit']

    # Validate required fields
    if not unit_data.get("name"):
        return {"message": "name field is required"}, 400
    
    if not unit_data.get("level_id"):
        return {"message": "level_id field is required"}, 400

    # Verify level exists
    level_id = unit_data.get("level_id")
    level = Level.query.get(level_id)
    if not level:
        return {"message": "Invalid level_id"}, 404

    unit_schema = UnitSchema()
    try:
        unit = unit_schema.load(unit_data)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.add(unit)
    db.session.commit()
    return unit_schema.dump(unit), 201

@unit_bp.route('/units/<int:id>', methods=['PUT'])
@jwt_required()
@response_wrapper
def update_unit(id):
    """
    PUT /units/<unit_id>

    Description:
    Update a single unit by ID.

    Path Parameters:
    - unit_id: int — The ID of the unit to update.

    Request JSON Body:
    {
        "unit": {
            "name": str,             # optional
            "level_id": int          # optional
        }
    }

    Returns:
    - 200: JSON object of the updated unit (marshmallow schema)
    - 400: If validation fails
    - 404: If unit or level not found
    """
    unit = Unit.query.get_or_404(id)
    data = request.get_json()
    if not data or 'unit' not in data:
        return {"message": "Unit data is required in 'unit' key"}, 400
    
    unit_data = data['unit']

    # If level_id is being updated, verify it exists
    if 'level_id' in unit_data:
        level_id = unit_data.get("level_id")
        level = Level.query.get(level_id)
        if not level:
            return {"message": "Invalid level_id"}, 404

    unit_schema = UnitSchema(partial=True)
    try:
        updated_unit = unit_schema.load(unit_data, instance=unit, partial=True)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.commit()
    return unit_schema.dump(updated_unit), 200

@unit_bp.route('/units/<int:id>', methods=['DELETE'])
@jwt_required()
@response_wrapper
def delete_unit(id):
    """
    DELETE /units/<unit_id>

    Description:
    Delete a single unit by ID. This will also delete all associated quizzes.

    Path Parameters:
    - unit_id: int — The ID of the unit to delete.

    Returns:
    - 204: No content (successful deletion)
    - 404: If unit not found
    """
    unit = Unit.query.get_or_404(id)
    db.session.delete(unit)
    db.session.commit()
    return '', 204

@unit_bp.route('/units/<int:unit_id>', methods=['GET'])
@jwt_required()
@response_wrapper
def get_unit(unit_id):
    """
    GET /units/<unit_id>

    Description:
    Get a single unit by ID.

    Path Parameters:
    - unit_id: int — The ID of the unit to retrieve.

    Returns:
    - 200: JSON object of the unit (marshmallow schema)
    - 404: If unit not found
    """
    unit = Unit.query.get_or_404(unit_id)
    unit_schema = UnitSchema()
    return unit_schema.dump(unit)