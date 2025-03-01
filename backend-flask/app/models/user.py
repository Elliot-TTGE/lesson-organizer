from app.db import db

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)
    last_login = db.Column(db.DateTime)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.Enum('admin', 'assistant', 'instructor', name='user_role'), nullable=False)