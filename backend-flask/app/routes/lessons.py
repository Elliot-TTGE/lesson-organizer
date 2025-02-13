from flask import Blueprint, request
from app.db import db
from app.models.lesson import Lesson
from app.models.schema import LessonSchema
from app.routes.utils import response_wrapper

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
        concepts_taught=lesson.get('concepts_taught', ''),
        additional_notes=lesson.get('additional_notes', '')
    )
    db.session.add(new_lesson)
    db.session.commit()
    return lesson_schema.dump(new_lesson)