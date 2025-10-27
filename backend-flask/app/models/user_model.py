from app.db import db
from app.models.base_model import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class User(BaseModel):
    __tablename__ = 'user'
    
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    last_login = db.Column(db.DateTime)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.Enum('admin', 'assistant', 'instructor', name='user_role'), nullable=False)
    fs_uniquifier = db.Column(db.String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    # Relationships
    owned_lessons = db.relationship(
        "Lesson",
        foreign_keys="Lesson.owner_id",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    
    shared_lessons = db.relationship(
        "Lesson",
        secondary="user_lesson",
        back_populates="collaborators"
    )
    
    user_lesson_shares = db.relationship(
        "UserLesson",
        back_populates="user"
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)
    
    def is_admin(self):
        """Check if user has admin privileges"""
        return self.role == 'admin'
    
    def can_access_user_data(self, target_user_id):
        """Check if user can access another user's data"""
        return self.is_admin() or self.id == target_user_id
    
    def can_edit_lesson(self, lesson):
        """Check if user can edit a specific lesson"""
        if self.is_admin() or lesson.owner_id == self.id:
            return True
        
        # Check if user has edit permission through sharing
        from app.models.user_lesson_model import UserLesson
        user_lesson = UserLesson.query.filter_by(
            user_id=self.id,
            lesson_id=lesson.id
        ).first()
        
        return user_lesson and user_lesson.permission_level in ['edit', 'manage']