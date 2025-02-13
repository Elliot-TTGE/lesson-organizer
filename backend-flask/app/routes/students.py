from flask import Blueprint, request
from app.main import db
from app.models.student import Student
from app.models.schema import StudentSchema
from app.routes.utils import response_wrapper

students_bp = Blueprint('students', __name__)

@students_bp.route('/students', methods=['GET'])
@response_wrapper
def get_students():
    students = Student.query.all()
    student_schema = StudentSchema(many=True)
    return student_schema.dump(students)

@students_bp.route('/students', methods=['POST'])
@response_wrapper
def create_student():
    data = request.get_json()
    student_schema = StudentSchema()
    student = student_schema.load(data)
    new_student = Student(name=student['name'])
    db.session.add(new_student)
    db.session.commit()
    return student_schema.dump(new_student)