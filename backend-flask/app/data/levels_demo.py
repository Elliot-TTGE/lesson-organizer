from app.models.level import Level
from app.models.student import Student
from app.db import db
from datetime import datetime, timezone, timedelta
import random

def load_demo_level():
    students = Student.query.all()
    levels = []

    for student in students:
        start_date_1 = datetime.now(timezone.utc)
        start_date_2 = start_date_1 + timedelta(weeks=4)
        
        level_1 = Level(
            student_id=student.id,
            start_date=start_date_1,
            level_category=f"{random.choice('ABCDEF')}{random.randint(1, 9)}"
        )
        
        level_2 = Level(
            student_id=student.id,
            start_date=start_date_2,
            level_category=f"{random.choice('ABCDEF')}{random.randint(1, 9)}"
        )
        
        levels.extend([level_1, level_2])

    for level in levels:
        db.session.add(level)
    db.session.commit()
