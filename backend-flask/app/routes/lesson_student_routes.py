from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.db import db
from app.models.lesson_student_model import LessonStudent
from app.models.lesson_model import Lesson
from app.models.student_model import Student
from app.schemas.schemas import LessonStudentSchema
from app.routes.utils import response_wrapper

lesson_student_bp = Blueprint('lesson_student', __name__)

@lesson_student_bp.route('/lesson-student', methods=['POST'])
@jwt_required()
@response_wrapper
def add_lesson_student():
    data = request.get_json()
    lesson_id = data.get("lesson_id")
    student_id = data.get("student_id")
    if not lesson_id or not student_id:
        return jsonify({"error": "lesson_id and student_id are required"}), 400

    # Check if lesson and student exist
    lesson = Lesson.query.get(lesson_id)
    student = Student.query.get(student_id)
    if not lesson or not student:
        return jsonify({"error": "Invalid lesson_id or student_id"}), 404

    # Prevent duplicate entries
    existing = LessonStudent.query.filter_by(lesson_id=lesson_id, student_id=student_id).first()
    if existing:
        return jsonify({"error": "This student is already assigned to the lesson"}), 409

    lesson_student = LessonStudent(lesson_id=lesson_id, student_id=student_id)
    db.session.add(lesson_student)
    db.session.commit()
    return LessonStudentSchema().dump(lesson_student), 201

@lesson_student_bp.route('/lesson-student/<int:id>', methods=['DELETE'])
@jwt_required()
@response_wrapper
def delete_lesson_student(id):
    lesson_student = LessonStudent.query.get_or_404(id)
    db.session.delete(lesson_student)
    db.session.commit()
    return '', 204

@lesson_student_bp.route('/lesson-student', methods=['GET'])
@jwt_required()
@response_wrapper
def get_lesson_students():
    lesson_id = request.args.get("lesson_id")
    student_id = request.args.get("student_id")
    query = LessonStudent.query
    if lesson_id:
        query = query.filter_by(lesson_id=lesson_id)
    if student_id:
        query = query.filter_by(student_id=student_id)
    lesson_students = query.all()
    return LessonStudentSchema(many=True).dump(lesson_students), 200