from app.models.student import Student
from app.db import db

def generate_demo_data():
    demo_students = [
        Student(name='John Doe'),
        Student(name='Jane Smith'),
        Student(name='Alice Johnson'),
        Student(name='Bob Brown'),
        Student(name="Alice Johnson"),
        Student(name="Bob Smith"),
        Student(name="Charlie Brown")
    ]
    
    for student in demo_students:
        db.session.add(student)
    
    db.session.commit()
