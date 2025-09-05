from app.models.lesson_model import Lesson
from app.models.user_model import User
from app.models.user_lesson_model import UserLesson
from app.db import db
from sqlalchemy import or_

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
            shared_lesson_ids = db.session.query(UserLesson.lesson_id).filter(
                UserLesson.user_id == user_id
            ).subquery()
            
            query = Lesson.query.filter(
                or_(
                    Lesson.owner_id == user_id,
                    Lesson.id.in_(shared_lesson_ids)
                )
            )
        
        return query.all()
    
    @staticmethod
    def get_lessons_for_user(requesting_user_id, target_user_id):
        """Get lessons for a specific user (with admin override)"""
        requesting_user = User.query.get(requesting_user_id)
        if not requesting_user:
            raise PermissionError("Invalid user")
        
        # Check if user can access the data
        if not requesting_user.can_access_user_data(target_user_id):
            raise PermissionError("Access denied")
        
        # Admin can see all lessons for any user
        if requesting_user.is_admin() and requesting_user.id != target_user_id:
            return Lesson.query.filter(
                or_(
                    Lesson.owner_id == target_user_id,
                    Lesson.owner_id.is_(None)  # Include existing lessons without owners
                )
            ).all()
        
        # Regular user or admin viewing their own lessons
        return LessonService.get_user_lessons(target_user_id)
    
    @staticmethod
    def share_lesson(lesson_id, owner_id, target_user_id, permission_level='view'):
        """Share a lesson with another user"""
        # Verify the lesson belongs to the owner or owner is admin
        owner = User.query.get(owner_id)
        lesson = Lesson.query.get(lesson_id)
        
        if not owner or not lesson:
            raise ValueError("Invalid lesson or user")
        
        if not owner.is_admin() and lesson.owner_id != owner_id:
            raise PermissionError("You can only share your own lessons")
        
        # Check if already shared
        existing_share = UserLesson.query.filter_by(
            user_id=target_user_id,
            lesson_id=lesson_id
        ).first()
        
        if existing_share:
            # Update permission level
            existing_share.permission_level = permission_level
        else:
            # Create new share
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
        
        if not owner.is_admin() and lesson.owner_id != owner_id:
            raise PermissionError("You can only unshare your own lessons")
        
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
        
        return lesson.can_be_accessed_by(user)
    
    @staticmethod
    def can_user_edit_lesson(user_id, lesson_id):
        """Check if a user can edit a specific lesson"""
        user = User.query.get(user_id)
        lesson = Lesson.query.get(lesson_id)
        
        if not user or not lesson:
            return False
        
        return lesson.can_be_edited_by(user)
    
    @staticmethod
    def assign_ownership_to_existing_lessons(default_owner_id):
        """Assign ownership to existing lessons that don't have an owner"""
        lessons_without_owner = Lesson.query.filter(Lesson.owner_id.is_(None)).all()
        
        for lesson in lessons_without_owner:
            lesson.owner_id = default_owner_id
        
        db.session.commit()
        return len(lessons_without_owner)
