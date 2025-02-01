from app.main import db
from app.models.lesson import Lesson
from datetime import datetime

def load_demo_data():
    # Check if there are any existing lessons in the database
    if Lesson.query.count() > 0:
        print("Database already has data. Skipping demo data loading.")
        return

    demo_lessons = [
        {
            "datetime": datetime(2023, 10, 1, 10, 0),
            "plan": "Introduction to Python",
            "concepts": "Variables, Data Types",
            "notes": "Bring laptops",
            "created_date": datetime.now()
        },
        {
            "datetime": datetime(2023, 10, 2, 14, 0),
            "plan": "Advanced Python",
            "concepts": "Decorators, Generators",
            "notes": "Review previous lesson",
            "created_date": datetime.now()
        },
        {
            "datetime": datetime(2023, 10, 3, 16, 0),
            "plan": "Data Science with Python",
            "concepts": "Pandas, NumPy",
            "notes": "Install required libraries",
            "created_date": datetime.now()
        },
    ]
    
    for lesson_data in demo_lessons:
        lesson = Lesson(
            datetime=lesson_data["datetime"],
            plan=lesson_data["plan"],
            concepts=lesson_data["concepts"],
            notes=lesson_data["notes"],
            created_date=lesson_data["created_date"]
        )
        db.session.add(lesson)
    
    db.session.commit()
    print("Demo data loaded successfully.")
