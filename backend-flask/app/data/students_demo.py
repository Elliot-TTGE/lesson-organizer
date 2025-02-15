from app.models.student import Student
from app.db import db
from datetime import datetime, timezone

def load_demo_student():
    # Check if there are any existing students in the database
    if Student.query.count() > 0:
        print("Database already has data. Skipping demo data loading.")
        return

    demo_students = [
        Student(first_name='John', last_name='Doe', created_date=datetime.now(timezone.utc), status='active'),
        Student(first_name='Jane', last_name='Smith', created_date=datetime.now(timezone.utc), status='inactive'),
        Student(first_name='Alice', last_name='Johnson', created_date=datetime.now(timezone.utc), status='hold'),
        Student(first_name='Bob', last_name='Brown', created_date=datetime.now(timezone.utc), status='trial'),
        Student(first_name='Alice', last_name='Johnson', created_date=datetime.now(timezone.utc), status='active'),
        Student(first_name='Bob', last_name='Smith', created_date=datetime.now(timezone.utc), status='inactive'),
        Student(first_name='Charlie', last_name='Brown', created_date=datetime.now(timezone.utc), status='hold')
    ]
    
    for student in demo_students:
        db.session.add(student)
    
    db.session.commit()
    print("Demo data loaded successfully.")
