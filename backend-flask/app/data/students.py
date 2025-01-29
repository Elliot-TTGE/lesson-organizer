from app.models.student import Student
from app.db import db

def load_demo_data():
    # Check if there are any existing students in the database
    if Student.query.count() > 0:
        print("Database already has data. Skipping demo data loading.")
        return

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
    print("Demo data loaded successfully.")
