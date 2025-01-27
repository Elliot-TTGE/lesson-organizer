from app.data.students import generate_demo_data as generate_student_data
from app.data.lessons import generate_demo_data as generate_lesson_data
from app.data.lesson_student import assign_students_to_lessons

def load_demo_data():
    generate_student_data()
    generate_lesson_data()
    assign_students_to_lessons()
