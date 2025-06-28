from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import db
from app.models.user_model import User
from app.schemas.schemas import UserSchema
from app.routes.utils import response_wrapper

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
@jwt_required()
@response_wrapper
def get_users():
    """
    GET /users

    Query Parameters:
    - id: int (optional) — Get a single user by ID.
    - email: str (optional) — Filter users by email (partial match).
    - role: str (optional) — Filter users by role.

    Returns:
    - 200: JSON array of users or single user object.
    - 404: If user not found (when using id).
    """
    user_id = request.args.get('id', type=int)
    email = request.args.get('email')
    role = request.args.get('role')

    # Get single user by ID
    if user_id:
        user = User.query.get_or_404(user_id)
        schema = UserSchema()
        return schema.dump(user), 200

    # Build query
    query = User.query

    # Filter by email (partial match)
    if email:
        query = query.filter(User.email.ilike(f'%{email}%'))

    # Filter by role
    if role:
        query = query.filter(User.role == role)

    # Order by email for consistent ordering
    query = query.order_by(User.email)

    users = query.all()
    schema = UserSchema(many=True)
    return schema.dump(users), 200

@user_bp.route('/users', methods=['POST'])
@jwt_required()
@response_wrapper
def create_user():
    """
    POST /users

    Description:
    Create a new user.

    Request JSON Body:
    {
        "user": {
            "first_name": str,       # required
            "last_name": str,        # required
            "email": str,            # required
            "password": str,         # required
            "role": str              # required (admin, assistant, instructor)
        }
    }

    Returns:
    - 201: JSON object of the created user (marshmallow schema)
    - 400: If validation fails or required fields are missing
    """
    data = request.get_json()
    if not data or 'user' not in data:
        return {"message": "User data is required in 'user' key"}, 400
    
    user_data = data['user']

    # Validate required fields
    required_fields = ['first_name', 'last_name', 'email', 'password', 'role']
    for field in required_fields:
        if not user_data.get(field):
            return {"message": f"{field} field is required"}, 400

    # Check if email already exists
    existing_user = User.query.filter_by(email=user_data.get('email')).first()
    if existing_user:
        return {"message": "Email already exists"}, 400

    schema = UserSchema()
    try:
        user = schema.load(user_data)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.add(user)
    db.session.commit()
    return schema.dump(user), 201

@user_bp.route('/users/<int:id>', methods=['PUT'])
@jwt_required()
@response_wrapper
def update_user(id):
    """
    PUT /users/<user_id>

    Description:
    Update a single user by ID.

    Path Parameters:
    - user_id: int — The ID of the user to update.

    Request JSON Body:
    {
        "user": {
            "first_name": str,       # optional
            "last_name": str,        # optional
            "email": str,            # optional
            "password": str,         # optional
            "role": str,             # optional
            "last_login": str        # optional, ISO date string
        }
    }

    Returns:
    - 200: JSON object of the updated user (marshmallow schema)
    - 400: If validation fails or email already exists
    - 404: If user not found
    """
    user = User.query.get_or_404(id)
    data = request.get_json()
    if not data or 'user' not in data:
        return {"message": "User data is required in 'user' key"}, 400
    
    user_data = data['user']

    # Check if email is being updated and if it already exists
    if 'email' in user_data and user_data.get('email') != user.email:
        existing_user = User.query.filter_by(email=user_data.get('email')).first()
        if existing_user:
            return {"message": "Email already exists"}, 400

    schema = UserSchema(partial=True)
    try:
        updated_user = schema.load(user_data, instance=user, partial=True)
    except Exception as e:
        return {"message": str(e)}, 400

    db.session.commit()
    return schema.dump(updated_user), 200

@user_bp.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
@response_wrapper
def delete_user(id):
    """
    DELETE /users/<user_id>

    Description:
    Delete a single user by ID.

    Path Parameters:
    - user_id: int — The ID of the user to delete.

    Returns:
    - 204: No content (successful deletion)
    - 404: If user not found
    """
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return '', 204
