from app.models.user_model import User
from app.models.student_status_model import StudentStatus
from app.models.curriculum_model import Curriculum
from app.models.level_model import Level
from app.models.unit_model import Unit
from app.models.quiz_model import Quiz
from app.models.student_lesson_quiz_model import StudentLessonQuiz
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

def delete_all_units_quizzes_and_results():
    """
    Debug function to delete all units, quizzes, and student lesson quiz results.
    WARNING: This will permanently delete all quiz data!
    """
    print("Deleting all student lesson quiz results...")
    StudentLessonQuiz.query.delete()
    
    print("Deleting all quizzes...")
    Quiz.query.delete()
    
    print("Deleting all units...")
    Unit.query.delete()
    
    db.session.commit()
    print("All units, quizzes, and student lesson quiz results have been deleted!")

def create_all_units():
    # Get all levels
    levels = Level.query.all()
    for level in levels:
        curriculum_name = level.curriculum.name
        
        if curriculum_name == "Interchange":
            # Determine unit range based on level suffix
            if level.name.endswith("-A"):
                # A levels: units 1-8
                unit_range = range(1, 9)
            elif level.name.endswith("-B"):
                # B levels: units 9-16
                unit_range = range(9, 17)
            else:
                # Default for other Interchange levels
                unit_range = range(1, 9)
                
            for unit_num in unit_range:
                unit_name = str(unit_num)
                existing = db.session.execute(
                    db.select(Unit).where(Unit.name == unit_name, Unit.level_id == level.id)
                ).scalar_one_or_none()
                if not existing:
                    db.session.add(Unit(name=unit_name, level_id=level.id))
                    
        elif curriculum_name == "Passages":
            # Passages: 12 units per level (1-12)
            for unit_num in range(1, 13):
                unit_name = str(unit_num)
                existing = db.session.execute(
                    db.select(Unit).where(Unit.name == unit_name, Unit.level_id == level.id)
                ).scalar_one_or_none()
                if not existing:
                    db.session.add(Unit(name=unit_name, level_id=level.id))
        else:
            # Default: 8 units (1-8)
            for unit_num in range(1, 9):
                unit_name = str(unit_num)
                existing = db.session.execute(
                    db.select(Unit).where(Unit.name == unit_name, Unit.level_id == level.id)
                ).scalar_one_or_none()
                if not existing:
                    db.session.add(Unit(name=unit_name, level_id=level.id))
    db.session.commit()

def create_all_quizzes():
    # Get all levels to create quizzes based on curriculum
    levels = Level.query.all()
    
    for level in levels:
        curriculum_name = level.curriculum.name
        
        if curriculum_name == "Interchange":
            # Interchange: Quiz every 2 units with max score of 25
            max_score = 25
            
            if level.name.endswith("-A"):
                # A levels (units 1-8): quizzes at units 2, 4, 6, 8
                quiz_units = [2, 4, 6, 8]
            elif level.name.endswith("-B"):
                # B levels (units 9-16): quizzes at units 10, 12, 14, 16
                quiz_units = [10, 12, 14, 16]
            else:
                # Default for other Interchange levels
                quiz_units = [2, 4, 6, 8]
                
            for unit_num in quiz_units:
                unit = db.session.execute(
                    db.select(Unit).where(Unit.name == str(unit_num), Unit.level_id == level.id)
                ).scalar_one_or_none()
                
                if unit:
                    quiz_name = f"{curriculum_name} {level.name} - Units {unit_num-1}-{unit_num}"
                        
                    existing = db.session.execute(
                        db.select(Quiz).where(Quiz.name == quiz_name, Quiz.unit_id == unit.id)
                    ).scalar_one_or_none()
                    if not existing:
                        db.session.add(Quiz(name=quiz_name, max_points=max_score, unit_id=unit.id))
                        
        elif curriculum_name == "Passages":
            # Passages: Quiz every unit (units 1-12) with max score of 50
            max_score = 50
            for unit_num in range(1, 13):
                unit = db.session.execute(
                    db.select(Unit).where(Unit.name == str(unit_num), Unit.level_id == level.id)
                ).scalar_one_or_none()
                
                if unit:
                    quiz_name = f"{curriculum_name} {level.name} - Unit {unit_num}"
                    existing = db.session.execute(
                        db.select(Quiz).where(Quiz.name == quiz_name, Quiz.unit_id == unit.id)
                    ).scalar_one_or_none()
                    if not existing:
                        db.session.add(Quiz(name=quiz_name, max_points=max_score, unit_id=unit.id))
            
            # Add Midterm and Final quizzes for Passages (tied to specific units)
            # Midterm tied to unit 6
            midterm_unit = db.session.execute(
                db.select(Unit).where(Unit.name == "6", Unit.level_id == level.id)
            ).scalar_one_or_none()
            
            if midterm_unit:
                midterm_name = f"{curriculum_name} {level.name} - Midterm"
                existing_midterm = db.session.execute(
                    db.select(Quiz).where(Quiz.name == midterm_name, Quiz.unit_id == midterm_unit.id)
                ).scalar_one_or_none()
                if not existing_midterm:
                    db.session.add(Quiz(name=midterm_name, max_points=max_score, unit_id=midterm_unit.id))
            
            # Final tied to unit 12
            final_unit = db.session.execute(
                db.select(Unit).where(Unit.name == "12", Unit.level_id == level.id)
            ).scalar_one_or_none()
            
            if final_unit:
                final_name = f"{curriculum_name} {level.name} - Final"
                existing_final = db.session.execute(
                    db.select(Quiz).where(Quiz.name == final_name, Quiz.unit_id == final_unit.id)
                ).scalar_one_or_none()
                if not existing_final:
                    db.session.add(Quiz(name=final_name, max_points=max_score, unit_id=final_unit.id))
    
    db.session.commit()



def create_all_data():
    create_admin_user()
    create_all_student_status()
    create_all_curriculums()
    create_all_levels()
    create_all_units()
    create_all_quizzes()
    reset_units_and_quizzes()

def reset_units_and_quizzes():
    """
    Debug function to delete and recreate all units and quizzes.
    This preserves student and level data but resets the quiz system.
    """
    delete_all_units_quizzes_and_results()
    create_all_units()
    create_all_quizzes()
    print("Units and quizzes have been reset and recreated!")


