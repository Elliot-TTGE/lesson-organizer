from marshmallow import Schema, fields, post_dump

class StudentSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str()
    created_date = fields.DateTime(required=True)
    status = fields.Str(required=True)
    lessons = fields.List(fields.Nested('LessonSchema', exclude=('students',)))
    quizzes = fields.List(fields.Nested('QuizSchema', exclude=('student',)))
    levels = fields.List(fields.Nested('LevelSchema', exclude=('student',)))

    @post_dump
    def add_utc_suffix(self, data, **kwargs):
        if 'created_date' in data and data['created_date']:
            data['created_date'] = data['created_date'] + 'Z'
        return data

class LessonSchema(Schema):
    id = fields.Int(dump_only=True)
    datetime = fields.DateTime(required=True)
    plan = fields.Str()
    concepts = fields.Str()
    created_date = fields.DateTime(dump_only=True)
    notes = fields.Str()
    students = fields.List(fields.Nested(StudentSchema, exclude=('lessons',)))
    quizzes = fields.List(fields.Nested('QuizSchema', exclude=('lesson',)))
    
    @post_dump
    def add_utc_suffix(self, data, **kwargs):
        if 'datetime' in data and data['datetime']:
            data['datetime'] = data['datetime'] + 'Z'
        if 'created_date' in data and data['created_date']:
            data['created_date'] = data['created_date'] + 'Z'
        return data

class QuizSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    datetime = fields.DateTime(required=True)
    score = fields.Float(required=True)
    notes = fields.Str()
    lesson_id = fields.Int(required=True)
    student_id = fields.Int(required=True)
    lesson = fields.Nested(LessonSchema, only=('id', 'datetime', 'plan', 'concepts'))
    student = fields.Nested(StudentSchema, only=('id', 'first_name', 'last_name', 'status'))

    @post_dump
    def add_utc_suffix(self, data, **kwargs):
        if 'datetime' in data and data['datetime']:
            data['datetime'] = data['datetime'] + 'Z'
        return data

class LevelSchema(Schema):
    id = fields.Int(dump_only=True)
    student_id = fields.Int(required=True)
    start_date = fields.DateTime(required=True)
    level_category = fields.Str(required=True)
    student = fields.Nested(StudentSchema, only=('id', 'first_name', 'last_name', 'status'))
    
    @post_dump
    def add_utc_suffix(self, data, **kwargs):
        if 'start_date' in data and data['start_date']:
            data['start_date'] = data['start_date'] + 'Z'
        return data

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    created_date = fields.DateTime(required=True)
    last_login = fields.DateTime()
    password = fields.Str(required=True)
    role = fields.Str(required=True)

    @post_dump
    def add_utc_suffix(self, data, **kwargs):
        if 'created_date' in data and data['created_date']:
            data['created_date'] = data['created_date'] + 'Z'
        if 'last_login' in data and data['last_login']:
            data['last_login'] = data['last_login'] + 'Z'
        return data