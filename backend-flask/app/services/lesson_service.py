from app.models.lesson_model import Lesson
from app.models.user_model import User
from app.models.user_lesson_model import UserLesson
from app.db import db
from sqlalchemy import or_

class PermissionLevel:
    VIEW = 'view'
    EDIT = 'edit'
    MANAGE = 'manage'
    
    @classmethod
    def all_levels(cls):
        return [cls.VIEW, cls.EDIT, cls.MANAGE]
    
    @classmethod
    def can_edit(cls, level):
        return level in [cls.EDIT, cls.MANAGE]
    
    @classmethod
    def can_manage(cls, level):
        return level == cls.MANAGE

class LessonService:
    @staticmethod
    def get_user_lessons(user_id, include_shared=True):
        """Get all lessons accessible to a user"""
        user = User.query.get(user_id)
        if not user:
            return []
        
        # Admin can see all lessons
        if user.is_admin():
            return Lesson.query.all()
        
        # Regular user sees owned lessons and optionally shared lessons
        query = Lesson.query.filter(Lesson.owner_id == user_id)
        
        if include_shared:
            # Get shared lesson IDs
            shared_lesson_ids = db.session.query(UserLesson.lesson_id).filter_by(user_id=user_id).subquery()
            query = query.union(
                Lesson.query.filter(Lesson.id.in_(shared_lesson_ids))
            )
        
        return query.all()
    
    @staticmethod
    def get_lessons_for_user(requesting_user_id, target_user_id, include_shared=True):
        """Get lessons for a specific user (with admin override)"""
        requesting_user = User.query.get(requesting_user_id)
        if not requesting_user:
            raise ValueError("Invalid requesting user")
        
        # Check if user can access the data
        if not requesting_user.can_access_user_data(target_user_id):
            raise PermissionError("Access denied")
        
        # Admin can see all lessons for any user
        if requesting_user.is_admin() and requesting_user.id != target_user_id:
            return LessonService.get_user_lessons(target_user_id, include_shared=include_shared)
        
        # Regular user or admin viewing their own lessons
        return LessonService.get_user_lessons(target_user_id, include_shared=include_shared)
    
    @staticmethod
    def share_lesson(lesson_id, owner_id, target_user_id, permission_level='view'):
        """Share a lesson with another user"""
        # Verify the lesson belongs to the owner or owner is admin
        owner = User.query.get(owner_id)
        lesson = Lesson.query.get(lesson_id)
        
        if not owner or not lesson:
            raise ValueError("Invalid lesson or user")
        
        if not LessonService.can_user_manage_lesson(owner_id, lesson_id):
            raise PermissionError("You don't have permission to share this lesson")
        
        # Validate permission level
        if permission_level not in PermissionLevel.all_levels():
            raise ValueError(f"Invalid permission level: {permission_level}")
        
        # Check if already shared
        existing_share = UserLesson.query.filter_by(
            user_id=target_user_id,
            lesson_id=lesson_id
        ).first()
        
        if existing_share:
            existing_share.permission_level = permission_level
        else:
            user_lesson = UserLesson(
                user_id=target_user_id,
                lesson_id=lesson_id,
                permission_level=permission_level
            )
            db.session.add(user_lesson)
        
        db.session.commit()
        return True
    
    @staticmethod
    def unshare_lesson(lesson_id, owner_id, target_user_id):
        """Remove lesson sharing"""
        owner = User.query.get(owner_id)
        lesson = Lesson.query.get(lesson_id)
        
        if not owner or not lesson:
            raise ValueError("Invalid lesson or user")
        
        if not LessonService.can_user_manage_lesson(owner_id, lesson_id):
            raise PermissionError("You don't have permission to unshare this lesson")
        
        user_lesson = UserLesson.query.filter_by(
            user_id=target_user_id,
            lesson_id=lesson_id
        ).first()
        
        if user_lesson:
            db.session.delete(user_lesson)
            db.session.commit()
        
        return True

    @staticmethod
    def can_user_access_lesson(user_id, lesson_id):
        """Check if a user can access a specific lesson"""
        user = User.query.get(user_id)
        lesson = Lesson.query.get(lesson_id)
        
        if not user or not lesson:
            return False
        
        # Owner can always access
        if lesson.owner_id == user_id:
            return True
        
        # Check shared permissions (any level allows access)
        user_lesson = UserLesson.query.filter_by(
            user_id=user_id,
            lesson_id=lesson_id
        ).first()
        
        if user_lesson:
            return True
        
        # System admin can access anything
        return user.is_admin()
    
    @staticmethod
    def can_user_edit_lesson(user_id, lesson_id):
        """Check if a user can edit a specific lesson"""
        user = User.query.get(user_id)
        lesson = Lesson.query.get(lesson_id)
        
        if not user or not lesson:
            return False
        
        # Owner can always edit
        if lesson.owner_id == user_id:
            return True
        
        # Check shared permissions
        user_lesson = UserLesson.query.filter_by(
            user_id=user_id,
            lesson_id=lesson_id
        ).first()
        
        if user_lesson:
            return PermissionLevel.can_edit(user_lesson.permission_level)
        
        # System admin can edit anything
        return user.is_admin()
    
    @staticmethod
    def can_user_manage_lesson(user_id, lesson_id):
        """Check if a user can manage a specific lesson (share, delete, etc.)"""
        user = User.query.get(user_id)
        lesson = Lesson.query.get(lesson_id)
        
        if not user or not lesson:
            return False
        
        # Owner can always manage
        if lesson.owner_id == user_id:
            return True
        
        # Check shared permissions
        user_lesson = UserLesson.query.filter_by(
            user_id=user_id,
            lesson_id=lesson_id
        ).first()
        
        if user_lesson:
            return PermissionLevel.can_manage(user_lesson.permission_level)
        
        # System admin can manage anything
        return user.is_admin()
    
    @staticmethod
    def assign_ownership_to_existing_lessons(default_owner_id):
        """Assign ownership to lessons that don't have an owner"""
        lessons_without_owner = Lesson.query.filter(Lesson.owner_id.is_(None)).all()
        count = 0
        
        for lesson in lessons_without_owner:
            lesson.owner_id = default_owner_id
            count += 1
        
        db.session.commit()
        return count
