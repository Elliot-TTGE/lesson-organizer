from app.main import db
from app.models.lesson import Lesson
from datetime import datetime, timezone

def load_demo_lesson():
    # Check if there are any existing lessons in the database
    if Lesson.query.count() > 0:
        print("Database already has data. Skipping demo data loading.")
        return

    demo_lessons = [
        {
            "datetime": datetime(2025, 10, 1, 13, 0, tzinfo=timezone.utc),
            "plan": "Introduction to Python",
            "concepts": "Variables, Data Types",
            "notes": "Bring laptops",
            "created_date": datetime.now(timezone.utc)
        },
        {
            "datetime": datetime(2025, 10, 2, 14, 30, tzinfo=timezone.utc),
            "plan": "Advanced Python",
            "concepts": "Decorators, Generators",
            "notes": "Review previous lesson",
            "created_date": datetime.now(timezone.utc)
        },
        {
            "datetime": datetime(2025, 10, 3, 16, 0, tzinfo=timezone.utc),
            "plan": "Data Science with Python",
            "concepts": "Pandas, NumPy",
            "notes": "Install required libraries",
            "created_date": datetime.now(timezone.utc)
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
