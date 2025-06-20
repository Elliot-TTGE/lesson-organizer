from app.data.demo.lessons_demo import load_demo_lesson
from app.data.demo.students_demo import load_demo_student
from app.data.demo.lesson_student_demo import assign_students_to_lessons
from app.data.demo.quizzes_demo import load_demo_quiz
from app.data.demo.levels_demo import load_demo_level
from app.data.demo.users_demo import load_demo_user

def load_demo_data():
    load_demo_student()
    load_demo_lesson()
    assign_students_to_lessons()
    load_demo_quiz()
    load_demo_level()
    load_demo_user()
