from flask import Blueprint, request, jsonify
from app.db import db
from app.models.lesson import Lesson
from app.models.schema import LessonSchema
from app.routes.utils import response_wrapper
from datetime import datetime, timezone

lessons_bp = Blueprint('lessons', __name__)

@lessons_bp.route('/lessons', methods=['GET'])
@response_wrapper
def get_lessons():
    lessons = Lesson.query.all()
    lesson_schema = LessonSchema(many=True)
    return lesson_schema.dump(lessons)

@lessons_bp.route('/lessons', methods=['POST'])
@response_wrapper
def create_lesson():
    data = request.get_json()
    lesson_schema = LessonSchema()
    lesson = lesson_schema.load(data)
    new_lesson = Lesson(
        datetime=lesson['datetime'],
        plan=lesson['plan'],
        concepts=lesson['concepts'],
        created_date=datetime.now(timezone.utc),
        notes=lesson['notes']
    )
    db.session.add(new_lesson)
    db.session.commit()
    return lesson_schema.dump(new_lesson), 201

@lessons_bp.route('/lessons/<int:id>', methods=['PUT'])
@response_wrapper
def update_lesson(id):
    lesson = Lesson.query.get_or_404(id)
    data = request.get_json()
    lesson_schema = LessonSchema()
    updated_lesson = lesson_schema.load(data, instance=lesson)
    db.session.commit()
    return lesson_schema.dump(updated_lesson)

@lessons_bp.route('/lessons/<int:id>', methods=['DELETE'])
def delete_lesson(id):
    lesson = Lesson.query.get_or_404(id)
    db.session.delete(lesson)
    db.session.commit()
    return jsonify({"message": "Lesson deleted successfully"}), 204