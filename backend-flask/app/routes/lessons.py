from flask import Blueprint, jsonify, request
from app.db import db
from app.models.lesson import Lesson
from app.models.schema import LessonSchema

lessons_bp = Blueprint('lessons', __name__)

@lessons_bp.route('/lessons', methods=['GET'])
def get_lessons():
    lessons = Lesson.query.all()
    lesson_schema = LessonSchema(many=True)
    return jsonify(lesson_schema.dump(lessons))

@lessons_bp.route('/lessons', methods=['POST'])
def create_lesson():
    data = request.get_json()
    lesson_schema = LessonSchema()
    lesson = lesson_schema.load(data)
    new_lesson = Lesson(
        datetime=lesson['datetime'],
        plan=lesson['plan'],
        concepts_taught=lesson.get('concepts_taught', ''),
        additional_notes=lesson.get('additional_notes', '')
    )
    db.session.add(new_lesson)
    db.session.commit()
    return jsonify(lesson_schema.dump(new_lesson)), 201