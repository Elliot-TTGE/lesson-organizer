from app.models.user_model import User
from app.models.student_status_model import StudentStatus
from app.models.curriculum_model import Curriculum
from app.models.level_model import Level
from app.models.unit_model import Unit
from app.models.quiz_model import Quiz
from app.db import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
import os
import uuid

def create_admin_user():
    admin_email = os.environ.get("ADMIN_EMAIL")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    admin_first_name = os.environ.get("ADMIN_FIRST_NAME")
    admin_last_name = os.environ.get("ADMIN_LAST_NAME")
    if not admin_email or not admin_password or not admin_first_name or not admin_last_name:
        raise Exception("Set ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_FIRST_NAME, and ADMIN_LAST_NAME environment variables.")

    user = User.query.filter_by(email=admin_email).first()
    if not user:
        user = User(
            first_name = admin_first_name,
            last_name = admin_last_name,
            created_date=datetime.now(timezone.utc),
            email = admin_email,
            password=generate_password_hash(admin_password),
            role="admin",
            fs_uniquifier=str(uuid.uuid4())
        )
        db.session.add(user)
        db.session.commit()

def create_all_student_status():
    statuses = ["Active", "Inactive", "Hold", "Future", "Trial"]
    for status in statuses:
        existing = StudentStatus.query.filter_by(name=status).first()
        if not existing:
            db.session.add(StudentStatus(name=status))
    db.session.commit()

def create_all_curriculums():
    curriculum_names = ["Interchange", "Passages"]
    for name in curriculum_names:
        existing = Curriculum.query.filter_by(name=name).first()
        if not existing:
            db.session.add(Curriculum(name=name))
    db.session.commit()

def create_all_levels():
    # Get curriculum objects by name
    interchange = Curriculum.query.filter_by(name="Interchange").first()
    passages = Curriculum.query.filter_by(name="Passages").first()

    # Only proceed if curriculums exist
    if interchange:
        interchange_levels = ["Intro-A", "Intro-B", "1-A", "1-B", "2-A", "2-B", "3-A", "3-B"]
        for level_name in interchange_levels:
            existing = db.session.execute(
                db.select(Level).where(Level.name == level_name, Level.curriculum_id == interchange.id)
            ).scalar_one_or_none()
            if not existing:
                db.session.add(Level(name=level_name, curriculum_id=interchange.id))

    if passages:
        passages_levels = ["1", "2"]
        for level_name in passages_levels:
            existing = db.session.execute(
                db.select(Level).where(Level.name == level_name, Level.curriculum_id == passages.id)
            ).scalar_one_or_none()
            if not existing:
                db.session.add(Level(name=level_name, curriculum_id=passages.id))

    db.session.commit()

def create_all_units():
    # Get all levels
    levels = Level.query.all()
    for level in levels:
        for i in range(1, 9):
            unit_name = str(i)
            existing = db.session.execute(
                db.select(Unit).where(Unit.name == unit_name, Unit.level_id == level.id)
            ).scalar_one_or_none()
            if not existing:
                db.session.add(Unit(name=unit_name, level_id=level.id))
    db.session.commit()

def create_all_quizzes():
    # For each unit with an even-numbered name, create a quiz
    units = Unit.query.all()
    for unit in units:
        # Only create a quiz for units with even-numbered names
        try:
            unit_number = int(unit.name)
        except ValueError:
            continue  # Skip units with non-integer names
        if unit_number % 2 == 0:
            quiz_name = f"Quiz {unit.name}"
            existing = db.session.execute(
                db.select(Quiz).where(Quiz.name == quiz_name, Quiz.unit_id == unit.id)
            ).scalar_one_or_none()
            if not existing:
                db.session.add(Quiz(name=quiz_name, max_points=100, unit_id=unit.id))
    db.session.commit()



def create_all_data():
    create_admin_user()
    create_all_student_status()
    create_all_curriculums()
    create_all_levels()
    create_all_units()
    create_all_quizzes()
    
    
