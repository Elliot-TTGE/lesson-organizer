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
    - id: int (optional) — Get a single unit by ID.
    - name: str (optional) — Filter units by name (partial match).
    - level_id: int (optional) — Filter units by level ID.

    Returns:
    - 200: JSON array of units or single unit object.
    - 404: If unit not found (when using id).
    """
    unit_id = request.args.get('id', type=int)
    name = request.args.get('name')
    level_id = request.args.get('level_id', type=int)

    # Get single unit by ID
    if unit_id:
        unit = Unit.query.get_or_404(unit_id)
        unit_schema = UnitSchema()
        return unit_schema.dump(unit), 200

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
        "name": str,             # required
        "level_id": int          # required
    }

    Returns:
    - 201: JSON object of the created unit (marshmallow schema)
    - 400: If validation fails or required fields are missing
    - 404: If level not found
    """
    data = request.get_json()

    # Validate required fields
    if not data.get("name"):
        return jsonify({"error": "name field is required"}), 400
    
    if not data.get("level_id"):
        return jsonify({"error": "level_id field is required"}), 400

    # Verify level exists
    level_id = data.get("level_id")
    level = Level.query.get(level_id)
    if not level:
        return jsonify({"error": "Invalid level_id"}), 404

    unit_schema = UnitSchema()
    unit = unit_schema.load(data)
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
        "name": str,             # optional
        "level_id": int          # optional
    }

    Returns:
    - 200: JSON object of the updated unit (marshmallow schema)
    - 400: If validation fails
    - 404: If unit or level not found
    """
    unit = Unit.query.get_or_404(id)
    data = request.get_json()

    # If level_id is being updated, verify it exists
    if 'level_id' in data:
        level_id = data.get("level_id")
        level = Level.query.get(level_id)
        if not level:
            return jsonify({"error": "Invalid level_id"}), 404

    unit_schema = UnitSchema()
    unit = unit_schema.load(data, instance=unit, partial=True)
    db.session.commit()
    return unit_schema.dump(unit), 200

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