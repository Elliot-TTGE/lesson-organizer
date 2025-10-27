from app.models.base_model import BaseModel
from app.db import db

class Lesson(BaseModel):
    __tablename__ = "lesson"

    datetime = db.Column(db.DateTime, nullable=False)
    plan = db.Column(db.String)
    concepts = db.Column(db.String)
    notes = db.Column(db.String)
    
    # User ownership and sharing
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # nullable for existing data

    # Relationships
    owner = db.relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="owned_lessons"
    )
    
    collaborators = db.relationship(
        "User",
        secondary="user_lesson",
        back_populates="shared_lessons"
    )
    
    user_shares = db.relationship(
        "UserLesson",
        back_populates="lesson"
    )
    
    students = db.relationship(
        "Student",
        secondary="lesson_student",
        back_populates="lessons"
    )
    
    def can_be_accessed_by(self, user):
        """Check if a user can access this lesson"""
        if user.is_admin():
            return True
        if self.owner_id == user.id:
            return True
        
        # Check if user has shared access
        from app.models.user_lesson_model import UserLesson
        user_lesson = UserLesson.query.filter_by(
            user_id=user.id,
            lesson_id=self.id
        ).first()
        
        return user_lesson is not None
    
    def can_be_edited_by(self, user):
        """Check if a user can edit this lesson"""
        if user.is_admin():
            return True
        if self.owner_id == user.id:
            return True
        
        # Check if user has edit permission through sharing
        from app.models.user_lesson_model import UserLesson
        user_lesson = UserLesson.query.filter_by(
            user_id=user.id,
            lesson_id=self.id
        ).first()
        
        return user_lesson and user_lesson.permission_level in ['edit', 'manage']