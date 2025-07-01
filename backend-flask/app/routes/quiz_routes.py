from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import db
from app.models.quiz_model import Quiz
from app.models.unit_model import Unit
from app.schemas.schemas import QuizSchema
from app.routes.utils import response_wrapper

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/quizzes', methods=['GET'])
@jwt_required()
@response_wrapper
def get_quizzes():
    """
    GET /quizzes

    Query Parameters:
    - id: int (optional) — Get a single quiz by ID.
    - name: str (optional) — Filter quizzes by name (partial match).
    - unit_id: int (optional) — Filter quizzes by unit ID.

    Returns:
    - 200: JSON array of quizzes or single quiz object.
    - 404: If quiz not found (when using id).
    """
    quiz_id = request.args.get('id', type=int)
    name = request.args.get('name')
    unit_id = request.args.get('unit_id', type=int)

    # Get single quiz by ID
    if quiz_id:
        quiz = Quiz.query.get_or_404(quiz_id)
        schema = QuizSchema()
        return schema.dump(quiz), 200

    # Build query
    query = Quiz.query

    # Filter by unit ID
    if unit_id:
        query = query.filter(Quiz.unit_id == unit_id)

    # Filter by name (partial match)
    if name:
        query = query.filter(Quiz.name.ilike(f'%{name}%'))

    # Order by unit_id, then by name for consistent ordering
    query = query.order_by(Quiz.unit_id, Quiz.name)

    quizzes = query.all()
    schema = QuizSchema(many=True)
    return schema.dump(quizzes), 200

#@quiz_bp.route('/quizzes', methods=['POST'])
@jwt_required()
@response_wrapper
def create_quiz():
    """
    POST /quizzes

    Description:
    Create a new quiz.

    Request JSON Body:
    {
        "quiz": {
            "name": str,             # required
            "max_points": int,       # required
            "unit_id": int           # optional
        }
    }

    Returns:
    - 201: JSON object of the created quiz (marshmallow schema)
    - 400: If validation fails or required fields are missing
    - 404: If unit not found (when unit_id provided)
    """
    data = request.get_json()
    if not data or 'quiz' not in data:
        return {"message": "Quiz data is required in 'quiz' key"}, 400
    
    quiz_data = data['quiz']

    # Validate required fields
    if not quiz_data.get("name"):
        return {"message": "name field is required"}, 400
    
    if quiz_data.get("max_points") is None:
        return {"message": "max_points field is required"}, 400

    # Verify unit exists (if provided)
    unit_id = quiz_data.get("unit_id")
    if unit_id:
        unit = Unit.query.get(unit_id)
        if not unit:
            return {"message": "Invalid unit_id"}, 404

    schema = QuizSchema()
    try:
        quiz = schema.load(quiz_data)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.add(quiz)
    db.session.commit()
    return schema.dump(quiz), 201

#@quiz_bp.route('/quizzes/<int:id>', methods=['PUT'])
@jwt_required()
@response_wrapper
def update_quiz(id):
    """
    PUT /quizzes/<quiz_id>

    Description:
    Update a single quiz by ID.

    Path Parameters:
    - quiz_id: int — The ID of the quiz to update.

    Request JSON Body:
    {
        "quiz": {
            "name": str,             # optional
            "max_points": int,       # optional
            "unit_id": int           # optional
        }
    }

    Returns:
    - 200: JSON object of the updated quiz (marshmallow schema)
    - 400: If validation fails
    - 404: If quiz or unit not found
    """
    quiz = Quiz.query.get_or_404(id)
    data = request.get_json()
    if not data or 'quiz' not in data:
        return {"message": "Quiz data is required in 'quiz' key"}, 400
    
    quiz_data = data['quiz']

    # If unit_id is being updated, verify it exists
    if 'unit_id' in quiz_data and quiz_data.get("unit_id"):
        unit_id = quiz_data.get("unit_id")
        unit = Unit.query.get(unit_id)
        if not unit:
            return {"message": "Invalid unit_id"}, 404

    schema = QuizSchema(partial=True)
    try:
        updated_quiz = schema.load(quiz_data, instance=quiz, partial=True)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.commit()
    return schema.dump(updated_quiz), 200

#@quiz_bp.route('/quizzes/<int:id>', methods=['DELETE'])
@jwt_required()
@response_wrapper
def delete_quiz(id):
    """
    DELETE /quizzes/<quiz_id>

    Description:
    Delete a single quiz by ID. This will also delete all associated student lesson quiz records.

    Path Parameters:
    - quiz_id: int — The ID of the quiz to delete.

    Returns:
    - 204: No content (successful deletion)
    - 404: If quiz not found
    """
    quiz = Quiz.query.get_or_404(id)
    db.session.delete(quiz)
    db.session.commit()
    return '', 204
