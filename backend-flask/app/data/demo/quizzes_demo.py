from app.main import db
from app.models.quiz import Quiz
from app.models.student import Student
from app.models.lesson import Lesson
from datetime import datetime, timedelta
import random

def load_demo_quiz():
    # Check if there are any existing quizzes in the database
    if Quiz.query.count() > 0:
        print("Database already has data. Skipping demo data loading.")
        return

    students = Student.query.all()
    lessons = Lesson.query.all()
    demo_quizzes = []

    # Create quizzes for each student every 3-5 weeks
    for student in students:
        quiz_date = datetime.now() - timedelta(weeks=random.randint(3, 5))
        for _ in range(3):  # Create 3 quizzes per student
            demo_quizzes.append({
                "name": f"Quiz for {student.first_name + ' ' + student.last_name}",
                "datetime": quiz_date,
                "score": random.uniform(50, 100),
                "notes": "Demo quiz notes",
                "lesson_id": random.choice(lessons).id,
                "student_id": student.id
            })
            quiz_date += timedelta(weeks=random.randint(3, 5))

    # Create one quiz associated with multiple students
    common_quiz_date = datetime.now() - timedelta(weeks=random.randint(3, 5))
    common_lesson_id = random.choice(lessons).id
    for student in students:
        demo_quizzes.append({
            "name": "Common Quiz",
            "datetime": common_quiz_date,
            "score": random.uniform(50, 100),
            "notes": "Common quiz for all students",
            "lesson_id": common_lesson_id,
            "student_id": student.id
        })

    for quiz_data in demo_quizzes:
        quiz = Quiz(
            name=quiz_data["name"],
            datetime=quiz_data["datetime"],
            score=quiz_data["score"],
            notes=quiz_data["notes"],
            lesson_id=quiz_data["lesson_id"],
            student_id=quiz_data["student_id"]
        )
        db.session.add(quiz)

    db.session.commit()
    print("Demo quizzes loaded successfully.")
