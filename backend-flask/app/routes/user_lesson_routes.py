from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import db
from app.models.user_lesson_model import UserLesson
from app.models.lesson_model import Lesson
from app.models.user_model import User
from app.schemas.schemas import UserLessonSchema
from app.services.lesson_service import LessonService, PermissionLevel
from app.routes.utils import response_wrapper, get_current_user

user_lesson_bp = Blueprint('user_lessons', __name__)

@user_lesson_bp.route('/user-lessons', methods=['GET'])
@jwt_required()
@response_wrapper
def get_user_lessons():
    """
    GET /user-lessons

    Query Parameters:
    - lesson_id: int (optional) — Filter by specific lesson ID
    - user_id: int (optional) — Filter by specific user ID (admin only)
    - permission_level: str (optional) — Filter by permission level (view|edit|manage)

    Returns:
    - 200: JSON array of user lesson relationships
    - 403: If user lacks permission to view user lessons
    """
    current_user = get_current_user()
    if not current_user:
        return {"message": "Invalid authentication"}, 401
    
    lesson_id = request.args.get('lesson_id', type=int)
    user_id = request.args.get('user_id', type=int)
    permission_level = request.args.get('permission_level')
    
    # Build base query
    query = UserLesson.query
    
    # Apply filters
    if lesson_id:
        query = query.filter(UserLesson.lesson_id == lesson_id)
        
        # Check if user can manage this lesson to view its shares
        if not current_user.is_admin():
            lesson = Lesson.query.get(lesson_id)
            if not lesson:
                return {"message": "Lesson not found"}, 404
            
            if not LessonService.can_user_manage_lesson(current_user.id, lesson_id):
                return {"message": "You don't have permission to view shares for this lesson"}, 403
    
    if user_id:
        # Only allow filtering by user_id if admin or requesting own data
        if not current_user.is_admin() and user_id != current_user.id:
            return {"message": "You can only view your own lesson shares"}, 403
        query = query.filter(UserLesson.user_id == user_id)
    elif not current_user.is_admin():
        # Non-admins can only see their own shares
        query = query.filter(UserLesson.user_id == current_user.id)
    
    if permission_level:
        if permission_level not in PermissionLevel.all_levels():
            return {"message": f"Invalid permission level. Must be one of: {', '.join(PermissionLevel.all_levels())}"}, 400
        query = query.filter(UserLesson.permission_level == permission_level)
    
    user_lessons = query.all()
    schema = UserLessonSchema(many=True)
    return {"user_lessons": schema.dump(user_lessons)}

@user_lesson_bp.route('/user-lessons', methods=['POST'])
@jwt_required()
@response_wrapper
def create_user_lesson():
    """
    POST /user-lessons

    Description:
    Share a lesson with a user by creating a UserLesson relationship.
    Only lesson owners, users with manage permission, and system admins can share lessons.

    Request JSON Body:
    {
        "user_lesson": {
            "lesson_id": int,              # required
            "user_id": int,                # required
            "permission_level": str        # required, "view"|"edit"|"manage"
        }
    }

    Returns:
    - 201: JSON object of the created user lesson relationship
    - 400: If validation fails or required fields are missing
    - 403: If user lacks permission to share the lesson
    - 404: If lesson or user not found
    - 409: If relationship already exists
    """
    current_user = get_current_user()
    if not current_user:
        return {"message": "Invalid authentication"}, 401
    
    data = request.get_json()
    if not data or 'user_lesson' not in data:
        return {"message": "User lesson data is required in 'user_lesson' key"}, 400
    
    user_lesson_data = data['user_lesson']
    
    lesson_id = user_lesson_data.get('lesson_id')
    user_id = user_lesson_data.get('user_id')
    permission_level = user_lesson_data.get('permission_level')
    
    # Validate required fields
    if not lesson_id or not user_id or not permission_level:
        return {"message": "lesson_id, user_id, and permission_level are required"}, 400
    
    # Validate permission level
    if permission_level not in PermissionLevel.all_levels():
        return {"message": f"Invalid permission level. Must be one of: {', '.join(PermissionLevel.all_levels())}"}, 400
    
    # Check if lesson and user exist
    lesson = Lesson.query.get(lesson_id)
    target_user = User.query.get(user_id)
    
    if not lesson:
        return {"message": "Lesson not found"}, 404
    if not target_user:
        return {"message": "User not found"}, 404
    
    # Check if current user can manage this lesson (unless admin)
    if not current_user.is_admin():
        if not LessonService.can_user_manage_lesson(current_user.id, lesson_id):
            return {"message": "You don't have permission to share this lesson"}, 403
    
    # Check if relationship already exists
    existing = UserLesson.query.filter_by(
        lesson_id=lesson_id,
        user_id=user_id
    ).first()
    
    if existing:
        return {"message": "Lesson is already shared with this user"}, 409
    
    # Create new user lesson relationship
    user_lesson = UserLesson(
        lesson_id=lesson_id,
        user_id=user_id,
        permission_level=permission_level
    )
    
    db.session.add(user_lesson)
    db.session.commit()
    
    schema = UserLessonSchema()
    return schema.dump(user_lesson), 201

@user_lesson_bp.route('/user-lessons/<int:user_lesson_id>', methods=['PUT'])
@jwt_required()
@response_wrapper
def update_user_lesson(user_lesson_id):
    """
    PUT /user-lessons/<user_lesson_id>

    Description:
    Update a user lesson relationship's permission level.
    Only lesson owners, users with manage permission, and system admins can update permissions.

    Path Parameters:
    - user_lesson_id: int — The ID of the user lesson relationship to update

    Request JSON Body:
    {
        "user_lesson": {
            "permission_level": str        # required, "view"|"edit"|"manage"
        }
    }

    Returns:
    - 200: JSON object of the updated user lesson relationship
    - 400: If validation fails or required fields are missing
    - 403: If user lacks permission to update the relationship
    - 404: If user lesson relationship not found
    """
    current_user = get_current_user()
    if not current_user:
        return {"message": "Invalid authentication"}, 401
    
    user_lesson = UserLesson.query.get_or_404(user_lesson_id)
    
    data = request.get_json()
    if not data or 'user_lesson' not in data:
        return {"message": "User lesson data is required in 'user_lesson' key"}, 400
    
    user_lesson_data = data['user_lesson']
    
    permission_level = user_lesson_data.get('permission_level')
    if not permission_level:
        return {"message": "permission_level is required"}, 400
    
    # Validate permission level
    if permission_level not in PermissionLevel.all_levels():
        return {"message": f"Invalid permission level. Must be one of: {', '.join(PermissionLevel.all_levels())}"}, 400
    
    # Check if current user can manage this lesson (unless admin)
    if not current_user.is_admin():
        if not LessonService.can_user_manage_lesson(current_user.id, user_lesson.lesson_id):
            return {"message": "You don't have permission to update this lesson sharing"}, 403
    
    # Update permission level
    user_lesson.permission_level = permission_level
    db.session.commit()
    
    schema = UserLessonSchema()
    return schema.dump(user_lesson)

@user_lesson_bp.route('/user-lessons/<int:user_lesson_id>', methods=['DELETE'])
@jwt_required()
@response_wrapper
def delete_user_lesson(user_lesson_id):
    """
    DELETE /user-lessons/<user_lesson_id>

    Description:
    Remove a lesson sharing relationship.
    - Lesson owners and users with manage permission can remove any sharing for their lessons
    - Users can remove lessons that are shared with them (unsubscribe)
    - System admins can remove any sharing relationship

    Path Parameters:
    - user_lesson_id: int — The ID of the user lesson relationship to delete

    Returns:
    - 204: No content if deletion is successful
    - 403: If user lacks permission to delete the relationship
    - 404: If user lesson relationship not found
    """
    current_user = get_current_user()
    if not current_user:
        return {"message": "Invalid authentication"}, 401
    
    user_lesson = UserLesson.query.get_or_404(user_lesson_id)
    
    # Check permissions - allow if:
    # 1. User is admin
    # 2. User can manage the lesson (owner or has manage permission)
    # 3. User is removing a lesson shared with them (unsubscribing)
    can_delete = False
    
    if current_user.is_admin():
        can_delete = True
    elif LessonService.can_user_manage_lesson(current_user.id, user_lesson.lesson_id):
        # Lesson owner or user with manage permission can remove sharing
        can_delete = True
    elif user_lesson.user_id == current_user.id:
        # User can remove lessons shared with them (unsubscribe)
        can_delete = True
    
    if not can_delete:
        return {"message": "You don't have permission to remove this lesson sharing"}, 403
    
    db.session.delete(user_lesson)
    db.session.commit()
    
    return '', 204

@user_lesson_bp.route('/user-lessons/<int:user_lesson_id>', methods=['GET'])
@jwt_required()
@response_wrapper
def get_user_lesson(user_lesson_id):
    """
    GET /user-lessons/<user_lesson_id>

    Description:
    Get a specific user lesson relationship.
    Users can view their own relationships, lesson managers can view relationships for their lessons,
    and system admins can view any relationship.

    Path Parameters:
    - user_lesson_id: int — The ID of the user lesson relationship to retrieve

    Returns:
    - 200: JSON object of the user lesson relationship
    - 403: If user lacks permission to view the relationship
    - 404: If user lesson relationship not found
    """
    current_user = get_current_user()
    if not current_user:
        return {"message": "Invalid authentication"}, 401
    
    user_lesson = UserLesson.query.get_or_404(user_lesson_id)
    
    # Check permissions
    can_view = False
    
    if current_user.is_admin():
        can_view = True
    elif user_lesson.user_id == current_user.id:
        # User can view their own relationships
        can_view = True
    elif LessonService.can_user_manage_lesson(current_user.id, user_lesson.lesson_id):
        # Lesson managers can view relationships for their lessons
        can_view = True
    
    if not can_view:
        return {"message": "You don't have permission to view this lesson sharing relationship"}, 403
    
    schema = UserLessonSchema()
    return schema.dump(user_lesson)
