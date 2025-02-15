from flask import Blueprint, request, jsonify
from app.main import db
from app.models.student import Student
from app.models.schema import StudentSchema
from app.routes.utils import response_wrapper
from datetime import datetime

students_bp = Blueprint('students', __name__)

@students_bp.route('/students', methods=['GET'])
@response_wrapper
def get_students():
    query_params = request.args.to_dict()
    query = Student.query

    for key, value in query_params.items():
        if hasattr(Student, key):
            query = query.filter(getattr(Student, key) == value)

    students = query.all()
    student_schema = StudentSchema(many=True)
    return student_schema.dump(students)

@students_bp.route('/students', methods=['POST'])
@response_wrapper
def create_student():
    data = request.get_json()
    student_schema = StudentSchema()
    student = student_schema.load(data)
    new_student = Student(
        name=student['name'],
        created_date=datetime.utcnow(),
        status=student['status']
    )
    db.session.add(new_student)
    db.session.commit()
    return student_schema.dump(new_student), 201

@students_bp.route('/students/<int:id>', methods=['PUT'])
@response_wrapper
def update_student(id):
    student = Student.query.get_or_404(id)
    data = request.get_json()
    student_schema = StudentSchema()
    updated_student = student_schema.load(data, instance=student)
    db.session.commit()
    return student_schema.dump(updated_student)

@students_bp.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted successfully"}), 204