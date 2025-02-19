from app.db import db

class Level(db.Model):
    __tablename__ = 'level'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    level_category = db.Column(db.String, nullable=False)
    
    student = db.relationship('Student', back_populates='levels')