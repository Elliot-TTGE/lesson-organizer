import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from flask_migrate import init, migrate, upgrade, stamp
from app.main import app, db
import sqlite3
from datetime import datetime

def add_default_values_to_existing_db():
    """Add default values to existing database before migration"""
    db_path = os.path.join('/app', 'instance', 'lesson_organizer.db')
    if not os.path.exists(db_path):
        return
    
    print("Adding default values to existing database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get current timestamp for default values
        now = datetime.now().isoformat()
        
        # Check if columns exist before adding them
        tables_to_update = [
            ('lesson', ['updated_date']),
            ('lesson_student', ['created_date', 'updated_date']),
            ('level', ['created_date', 'updated_date']),
            ('quiz', ['created_date', 'updated_date']),
            ('student', ['updated_date']),
            ('user', ['updated_date'])
        ]
        
        for table_name, columns in tables_to_update:
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                continue
                
            for column in columns:
                # Check if column already exists
                cursor.execute(f"PRAGMA table_info({table_name})")
                existing_columns = [row[1] for row in cursor.fetchall()]
                
                if column not in existing_columns:
                    print(f"Adding {column} to {table_name} with default value...")
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} DATETIME DEFAULT '{now}'")
        
        conn.commit()
        print("Default values added successfully.")
        
    except Exception as e:
        print(f"Warning: Could not add default values: {e}")
        conn.rollback()
    finally:
        conn.close()

def run_migration():
    with app.app_context():
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        
        # Check if we have an existing database - in Docker it's mounted at /app/instance
        db_path = os.path.join('/app', 'instance', 'lesson_organizer.db')
        has_existing_db = os.path.exists(db_path)
        print(f"Checking for existing database at: {db_path}")
        print(f"Database exists: {has_existing_db}")
        
        # Initialize migrations only if directory doesn't exist
        if not os.path.exists(migrations_dir):
            print("Initializing migrations directory...")
            init()
            
            if has_existing_db:
                print("Found existing database. Preparing for migration...")
                # Add default values to existing database first
                add_default_values_to_existing_db()
                
                print("Creating initial migration...")
                # Create initial migration based on current models
                result = migrate(message="Initial migration from existing database")
                
                print("Migration file created successfully.")
                print("Applying migration to create new tables...")
                upgrade()
                print("Migration setup complete! Database has been updated with new schema.")
                print("The existing data has been preserved and new columns added with default values.")
            else:
                print("No existing database found. Creating initial migration...")
                migrate(message="Initial database schema")
                
                print("Applying initial migration...")
                upgrade()
        else:
            print("Migrations directory already exists. Skipping migration setup.")
            if has_existing_db:
                print("Database exists. Migration should have been completed previously.")
            else:
                print("Creating and applying migration...")
                migrate(message="Database schema")
                upgrade()
        
        print("Migration process complete!")

if __name__ == "__main__":
    run_migration()