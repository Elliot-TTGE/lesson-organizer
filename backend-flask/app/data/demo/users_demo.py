from app.models.user import User
from app.db import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
import uuid

def load_demo_user():
    demo_users = [
        {
            'first_name': 'Admin',
            'last_name': 'User',
            'email': 'admin123@test',
            'password': 'admin123',
            'role': 'admin'
        },
        {
            'first_name': 'Assistant',
            'last_name': 'User',
            'email': 'assistant123@test',
            'password': 'assistant123',
            'role': 'assistant'
        },
        {
            'first_name': 'Instructor',
            'last_name': 'User',
            'email': 'instructor123@test',
            'password': 'instructor123',
            'role': 'instructor'
        }
    ]

    for user_data in demo_users:
        user = User.query.filter_by(email=user_data['email']).first()
        if not user:
            user = User(
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                created_date=datetime.now(timezone.utc),
                last_login=datetime.now(timezone.utc),
                email=user_data['email'],
                password=generate_password_hash(user_data['password']),
                role=user_data['role'],
                fs_uniquifier=str(uuid.uuid4())
            )
            db.session.add(user)
    db.session.commit()

