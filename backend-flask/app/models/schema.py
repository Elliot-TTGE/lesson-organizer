from marshmallow import Schema, fields

class StudentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    created_date = fields.DateTime(required=True)
    status = fields.Str(required=True)
    lessons = fields.List(fields.Nested('LessonSchema', exclude=('students',)))
    quizzes = fields.List(fields.Nested('QuizSchema', exclude=('student',)))
    levels = fields.List(fields.Nested('LevelSchema', exclude=('student',)))

class LessonSchema(Schema):
    id = fields.Int(dump_only=True)
    datetime = fields.DateTime(required=True)
    plan = fields.Str(required=True)
    concepts = fields.Str(required=True)
    created_date = fields.DateTime(required=True)
    notes = fields.Str()
    students = fields.List(fields.Nested(StudentSchema, exclude=('lessons',)))
    quizzes = fields.List(fields.Nested('QuizSchema', exclude=('lesson',)))

class QuizSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    datetime = fields.DateTime(required=True)
    score = fields.Float(required=True)
    notes = fields.Str()
    lesson_id = fields.Int(required=True)
    student_id = fields.Int(required=True)
    lesson = fields.Nested(LessonSchema, only=('id', 'datetime', 'plan', 'concepts'))
    student = fields.Nested(StudentSchema, only=('id', 'name', 'status'))

class LevelSchema(Schema):
    id = fields.Int(dump_only=True)
    student_id = fields.Int(required=True)
    start_date = fields.DateTime(required=True)
    level_category = fields.Str(required=True)
    student = fields.Nested(StudentSchema, only=('id', 'name', 'status'))

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    created_date = fields.DateTime(required=True)
    last_login = fields.DateTime()
    password = fields.Str(required=True)
    role = fields.Str(required=True)