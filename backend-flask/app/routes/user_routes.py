from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import db
from app.models.user_model import User
from app.schemas.schemas import UserSchema
from app.routes.utils import response_wrapper, get_current_user

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
@jwt_required()
@response_wrapper
def get_users():
    """
    GET /users

    Query Parameters:
    - email: str (optional) — Filter users by email (partial match).
    - role: str (optional) — Filter users by role.

    Returns:
    - 200: JSON array of users.
    - 403: If user is not admin
    """
    current_user = get_current_user()
    
    # Only admins can view all users
    if not current_user.is_admin():
        return {"message": "Admin access required"}, 403
    
    email = request.args.get('email')
    role = request.args.get('role')

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
    - 403: If user is not admin
    """
    current_user = get_current_user()
    
    # Only admins can create users
    if not current_user.is_admin():
        return {"message": "Admin access required"}, 403
    
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

    # Create new user
    user = User(
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        email=user_data['email'],
        role=user_data['role']
    )
    user.set_password(user_data['password'])

    db.session.add(user)
    db.session.commit()
    
    schema = UserSchema()
    return schema.dump(user), 201

@user_bp.route('/users/<int:id>', methods=['PUT'])
@jwt_required()
@response_wrapper
def update_user(id):
    """
    PUT /users/<user_id>

    Description:
    Update a single user by ID. Users can only change their own passwords.

    Path Parameters:
    - user_id: int — The ID of the user to update.

    Request JSON Body:
    {
        "user": {
            "first_name": str,       # optional
            "last_name": str,        # optional
            "email": str,            # optional
            "password": str,         # optional (only for own account)
            "role": str,             # optional (admin only)
            "last_login": str        # optional, ISO date string
        }
    }

    Returns:
    - 200: JSON object of the updated user (marshmallow schema)
    - 400: If validation fails or email already exists
    - 403: If user lacks permission to update this user or tries to change another user's password
    - 404: If user not found
    """
    current_user = get_current_user()
    user = User.query.get_or_404(id)
    
    # Check if current user can access this user's data
    if not current_user.can_access_user_data(user.id):
        return {"message": "Insufficient permissions"}, 403
    
    data = request.get_json()
    if not data or 'user' not in data:
        return {"message": "User data is required in 'user' key"}, 400
    
    user_data = data['user']

    # Check if email is being updated and if it already exists
    if 'email' in user_data and user_data.get('email') != user.email:
        existing_user = User.query.filter_by(email=user_data.get('email')).first()
        if existing_user:
            return {"message": "Email already exists"}, 400

    # Update user fields
    if 'first_name' in user_data:
        user.first_name = user_data['first_name']
    if 'last_name' in user_data:
        user.last_name = user_data['last_name']
    if 'email' in user_data:
        user.email = user_data['email']
    if 'role' in user_data:
        # Only admins can change roles
        if not current_user.is_admin():
            return {"message": "Admin access required to change role"}, 403
        
        # Prevent admins from changing their own role
        if user.id == current_user.id:
            return {"message": "Cannot change your own role"}, 403
        
        # Prevent demoting the last admin (check if this would be the last admin)
        if user.role == 'admin' and user_data['role'] != 'admin':
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                return {"message": "Cannot demote the last admin in the system"}, 403
        
        user.role = user_data['role']
    if 'password' in user_data:
        # Only allow users to change their own password, not other users' passwords
        if current_user.id != user.id:
            return {"message": "Cannot change another user's password"}, 403
        user.set_password(user_data['password'])

    db.session.commit()
    
    schema = UserSchema()
    return schema.dump(user), 200

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
    - 403: If user is not admin
    - 404: If user not found
    """
    current_user = get_current_user()
    
    # Only admins can delete users
    if not current_user.is_admin():
        return {"message": "Admin access required"}, 403
    
    user = User.query.get_or_404(id)
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        return {"message": "Cannot delete your own account"}, 400
    
    # Prevent deleting the last admin
    if user.role == 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            return {"message": "Cannot delete the last admin in the system"}, 403
    
    db.session.delete(user)
    db.session.commit()
    return '', 204

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@response_wrapper
def get_user(user_id):
    """
    GET /users/<user_id>

    Description:
    Get a single user by ID.

    Path Parameters:
    - user_id: int — The ID of the user to retrieve.

    Returns:
    - 200: JSON object of the user (marshmallow schema)
    - 403: If user lacks permission to view this user
    - 404: If user not found
    """
    current_user = get_current_user()
    user = User.query.get_or_404(user_id)
    
    # Check if current user can access this user's data
    if not current_user.can_access_user_data(user.id):
        return {"message": "Insufficient permissions"}, 403
    
    schema = UserSchema()
    return schema.dump(user), 200

@user_bp.route('/users/me', methods=['GET'])
@jwt_required()
@response_wrapper
def get_current_user_profile():
    """
    GET /users/me

    Description:
    Get the current user's profile information.

    Returns:
    - 200: JSON object of the current user
    """
    current_user = get_current_user()
    schema = UserSchema()
    return schema.dump(current_user), 200
