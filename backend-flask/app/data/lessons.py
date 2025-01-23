from app.models.lesson import Lesson  # Assuming Lesson model is defined in app.models.lesson
from app.db import db  
from datetime import datetime  # Import datetime

def generate_demo_data():
    demo_lessons = [
        {
            "datetime": datetime(2023, 10, 1, 10, 0),
            "plan": "Introduction to Python",
            "concepts_taught": "Variables, Data Types",
            "additional_notes": "Bring laptops",
        },
        {
            "datetime": datetime(2023, 10, 2, 14, 0),
            "plan": "Advanced Python",
            "concepts_taught": "Decorators, Generators",
            "additional_notes": "Review previous lesson",
        },
        {
            "datetime": datetime(2023, 10, 3, 16, 0),
            "plan": "Data Science with Python",
            "concepts_taught": "Pandas, NumPy",
            "additional_notes": "Install required libraries",
        },
    ]
    
    for lesson_data in demo_lessons:
        lesson = Lesson(
            datetime=lesson_data["datetime"],
            plan=lesson_data["plan"],
            concepts_taught=lesson_data["concepts_taught"],
            additional_notes=lesson_data["additional_notes"]
        )
        db.session.add(lesson)
    
    db.session.commit()
