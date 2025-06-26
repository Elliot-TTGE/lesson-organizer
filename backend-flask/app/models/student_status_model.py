from app.db import db

class StudentStatus(db.Model):
    __tablename__ = "student_status"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
