from marshmallow import Schema, fields

class StudentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class LessonSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Str(required=True)
    time = fields.Str(required=True)
    plan = fields.Str(required=True)
    concepts_taught = fields.Str()
    additional_notes = fields.Str()
    students = fields.List(fields.Nested(StudentSchema))