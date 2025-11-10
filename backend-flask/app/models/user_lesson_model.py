from app.models.base_model import BaseModel
from app.db import db
from sqlalchemy.orm import validates

class UserLesson(BaseModel):
    __tablename__ = "user_lesson"
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id', ondelete='CASCADE'), nullable=False)
    
    # Permission levels for sharing features
    permission_level = db.Column(
        db.Enum('view', 'edit', 'manage', name='permission_level'), 
        default='view', 
        nullable=False
    )
    shared_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Ensure unique user-lesson combinations
    __table_args__ = (
        db.UniqueConstraint('user_id', 'lesson_id', name='unique_user_lesson'),
    )
    
    user = db.relationship("User", back_populates="user_lesson_shares")
    lesson = db.relationship("Lesson", back_populates="user_shares")

    @validates('user_id', 'lesson_id')
    def validate_not_owner(self, key, value):
        """Prevent sharing a lesson with its owner"""
        # Only validate when both user_id and lesson_id are set
        if hasattr(self, 'user_id') and hasattr(self, 'lesson_id'):
            from app.models.lesson_model import Lesson
            lesson = Lesson.query.get(self.lesson_id)
            if lesson and lesson.owner_id == self.user_id:
                raise ValueError("Cannot share a lesson with its owner")
        return value

