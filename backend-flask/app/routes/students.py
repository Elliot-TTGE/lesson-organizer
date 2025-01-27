from flask import Blueprint, jsonify, request
from app.main import db
from app.models.student import Student
from app.models.schema import StudentSchema

students_bp = Blueprint('students', __name__)

@students_bp.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    student_schema = StudentSchema(many=True)
    return jsonify(student_schema.dump(students))

@students_bp.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    student_schema = StudentSchema()
    student = student_schema.load(data)
    new_student = Student(name=student['name'])
    db.session.add(new_student)
    db.session.commit()
    return jsonify(student_schema.dump(new_student)), 201