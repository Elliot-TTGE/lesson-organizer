from app.schemas.base_schema import BaseSchema
from app.models.student_model import Student
from app.models.lesson_student_model import LessonStudent
from app.models.student_status_model import StudentStatus 
from app.models.student_status_history_model import StudentStatusHistory
from app.models.curriculum_model import Curriculum
from app.models.level_model import Level
from app.models.unit_model import Unit
from app.models.student_level_history import StudentLevelHistory
from app.models.quiz_model import Quiz
from app.models.student_lesson_quiz_model import StudentLessonQuiz
from app.models.user_model import User
from app.models.stock_image_model import StockImage

class StudentSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Student

class LessonStudentSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = LessonStudent

class StudentStatusSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = StudentStatus

class StudentStatusHistorySchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = StudentStatusHistory
    # exclude = ("student",)  # Prevent duplicate Student during serialization

class CurriculumSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Curriculum

class LevelSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Level

class UnitSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Unit

class StudentLevelHistorySchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = StudentLevelHistory

class QuizSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Quiz

class StudentLessonQuizSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = StudentLessonQuiz

class UserSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = User

class StockImageSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = StockImage



