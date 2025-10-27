from app.models.base_model import BaseModel
from app.db import db

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
