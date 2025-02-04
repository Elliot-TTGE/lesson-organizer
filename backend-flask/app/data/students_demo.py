from app.models.student import Student
from app.db import db
from datetime import datetime, timezone

def load_demo_student():
    # Check if there are any existing students in the database
    if Student.query.count() > 0:
        print("Database already has data. Skipping demo data loading.")
        return

    demo_students = [
        Student(name='John Doe', created_date=datetime.now(timezone.utc), status='active'),
        Student(name='Jane Smith', created_date=datetime.now(timezone.utc), status='inactive'),
        Student(name='Alice Johnson', created_date=datetime.now(timezone.utc), status='hold'),
        Student(name='Bob Brown', created_date=datetime.now(timezone.utc), status='trial'),
        Student(name="Alice Johnson", created_date=datetime.now(timezone.utc), status='active'),
        Student(name="Bob Smith", created_date=datetime.now(timezone.utc), status='inactive'),
        Student(name="Charlie Brown", created_date=datetime.now(timezone.utc), status='hold')
    ]
    
    for student in demo_students:
        db.session.add(student)
    
    db.session.commit()
    print("Demo data loaded successfully.")
