from app.models.user import User
from app.db import db
from datetime import datetime, timezone

def load_demo_user():
    demo_users = [
        User(
            first_name='Admin',
            last_name='User',
            created_date=datetime.now(timezone.utc),
            last_login=datetime.now(timezone.utc),
            password='admin123',
            role='admin'
        ),
        User(
            first_name='Assistant',
            last_name='User',
            created_date=datetime.now(timezone.utc),
            last_login=datetime.now(timezone.utc),
            password='assistant123',
            role='assistant'
        ),
        User(
            first_name='Instructor',
            last_name='User',
            created_date=datetime.now(timezone.utc),
            last_login=datetime.now(timezone.utc),
            password='instructor123',
            role='instructor'
        )
    ]

    for user in demo_users:
        db.session.add(user)
    db.session.commit()

