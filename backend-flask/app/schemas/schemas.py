from app.schemas.base_schema import BaseSchema
from app.models.student_model import Student
from app.models.lesson_student_model import LessonStudent
from app.models.student_status_model import StudentStatus 
from app.models.student_status_history_model import StudentStatusHistory
from app.models.curriculum_model import Curriculum
from app.models.level_model import Level
from app.models.unit_model import Unit
from app.models.student_level_history_model import StudentLevelHistory
from app.models.quiz_model import Quiz
from app.models.student_lesson_quiz_model import StudentLessonQuiz
from app.models.user_model import User
from app.models.stock_image_model import StockImage
from app.models.lesson_model import Lesson
from app.models.user_lesson_model import UserLesson
from marshmallow import fields
from marshmallow_sqlalchemy.fields import Nested

class StudentSchema(BaseSchema):
    # Nested relationships - avoiding circular references with dump_only
    lessons = Nested('LessonSchema', many=True, dump_only=True, exclude=['students'])
    status_history = Nested('StudentStatusHistorySchema', many=True, dump_only=True)
    level_history = Nested('StudentLevelHistorySchema', many=True, dump_only=True)
    quizzes = Nested('StudentLessonQuizSchema', many=True, dump_only=True)
    
    class Meta(BaseSchema.Meta):
        model = Student

class LessonStudentSchema(BaseSchema):
    # Nested relationships to show full objects instead of just IDs
    lesson = Nested('LessonSchema', dump_only=True, exclude=['students'])
    student = Nested('StudentSchema', dump_only=True, exclude=['lessons'])
    
    # Keep the foreign key fields for loading/creation
    lesson_id = fields.Integer(required=True, allow_none=False)
    student_id = fields.Integer(required=True, allow_none=False)
    
    class Meta(BaseSchema.Meta):
        model = LessonStudent

class StudentStatusSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = StudentStatus

class StudentStatusHistorySchema(BaseSchema):
    # Nested relationships to show full objects
    student = Nested('StudentSchema', dump_only=True, exclude=['status_history', 'lessons'])
    status = Nested('StudentStatusSchema', dump_only=True)
    
    # Keep the foreign key fields for loading/creation
    student_id = fields.Integer(required=True, allow_none=False)
    status_id = fields.Integer(required=True, allow_none=False)
    changed_at = fields.DateTime(required=True, allow_none=False)
    
    class Meta(BaseSchema.Meta):
        model = StudentStatusHistory
    # exclude = ("student",)  # Prevent duplicate Student during serialization

class LessonSchema(BaseSchema):
    # Nested relationships - avoiding circular references with dump_only
    students = Nested('StudentSchema', many=True, dump_only=True, exclude=['lessons'])
    owner = Nested('UserRelationshipSchema', dump_only=True)
    user_shares = Nested('UserLessonSchema', many=True, dump_only=True, exclude=['lesson'])
    
    class Meta(BaseSchema.Meta):
        model = Lesson

class CurriculumSchema(BaseSchema):
    # Nested relationships
    levels = Nested('LevelSchema', many=True, dump_only=True, exclude=['curriculum'])
    
    class Meta(BaseSchema.Meta):
        model = Curriculum

class LevelSchema(BaseSchema):
    # Nested relationships
    curriculum = Nested('CurriculumSchema', dump_only=True, exclude=['levels'])
    student_level_history = Nested('StudentLevelHistorySchema', many=True, dump_only=True, exclude=['level'])
    units = Nested('UnitSchema', many=True, dump_only=True, exclude=['level'])
    
    class Meta(BaseSchema.Meta):
        model = Level

class UnitSchema(BaseSchema):
    # Nested relationships
    level = Nested('LevelSchema', dump_only=True, exclude=['units'])
    quizzes = Nested('QuizSchema', many=True, dump_only=True, exclude=['unit'])
    
    class Meta(BaseSchema.Meta):
        model = Unit

class StudentLevelHistorySchema(BaseSchema):
    # Nested relationships to show full objects
    student = Nested('StudentSchema', dump_only=True, exclude=['level_history', 'lessons'])
    level = Nested('LevelSchema', dump_only=True)
    
    # Keep the foreign key fields for loading/creation
    student_id = fields.Integer(required=True, allow_none=False)
    level_id = fields.Integer(required=True, allow_none=False)
    start_date = fields.DateTime(required=True, allow_none=False)
    
    class Meta(BaseSchema.Meta):
        model = StudentLevelHistory

class QuizSchema(BaseSchema):
    # Nested relationships
    unit = Nested('UnitSchema', dump_only=True, exclude=['quizzes'])
    # Remove circular relationships - access through StudentLessonQuiz instead
    
    class Meta(BaseSchema.Meta):
        model = Quiz

class StudentLessonQuizSchema(BaseSchema):
    # Nested relationships to show full objects
    student = Nested('StudentSchema', dump_only=True, exclude=['lessons', 'quizzes'])
    lesson = Nested('LessonSchema', dump_only=True, exclude=['students'])
    quiz = Nested('QuizSchema', dump_only=True)
    
    # Keep the foreign key fields for loading/creation
    student_id = fields.Integer(required=True, allow_none=False)
    lesson_id = fields.Integer(required=True, allow_none=False)
    quiz_id = fields.Integer(allow_none=True)  # This is nullable in the model
    points = fields.Integer(allow_none=True)
    notes = fields.String(allow_none=True)
    
    class Meta(BaseSchema.Meta):
        model = StudentLessonQuiz

class UserSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = User

class UserRelationshipSchema(BaseSchema):
    """Schema for User when used as a relationship - excludes private fields"""
    class Meta(BaseSchema.Meta):
        model = User
        # Only include public fields when user is a relationship
        fields = ('id', 'first_name', 'last_name', 'email', 'role', 'created_date', 'updated_date')

class UserLessonSchema(BaseSchema):
    # Nested relationships to show full objects instead of just IDs
    user = Nested('UserRelationshipSchema', dump_only=True)
    lesson = Nested('LessonSchema', dump_only=True, exclude=['user_shares'])
    
    # Keep the foreign key fields for loading/creation
    user_id = fields.Integer(required=True, allow_none=False)
    lesson_id = fields.Integer(required=True, allow_none=False)
    permission_level = fields.String(required=True, allow_none=False)
    
    class Meta(BaseSchema.Meta):
        model = UserLesson

class StockImageSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = StockImage



