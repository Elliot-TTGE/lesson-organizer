# Import all models here to ensure they're registered with SQLAlchemy
# This is required for Flask-Migrate to detect all models
from .user_model import User
from .user_lesson_model import UserLesson
from .curriculum_model import Curriculum
from .lesson_model import Lesson
from .lesson_student_model import LessonStudent
from .level_model import Level
from .quiz_model import Quiz
from .stock_image_model import StockImage
from .student_lesson_quiz_model import StudentLessonQuiz
from .student_level_history_model import StudentLevelHistory
from .student_model import Student
from .student_status_history_model import StudentStatusHistory
from .student_status_model import StudentStatus
from .unit_model import Unit

ALL_MODELS = [
    User,
    UserLesson,
    Curriculum,
    Lesson,
    LessonStudent,
    Level,
    Quiz,
    StockImage,
    StudentLessonQuiz,
    StudentLevelHistory,
    Student,
    StudentStatusHistory,
    StudentStatus,
    Unit,
]
