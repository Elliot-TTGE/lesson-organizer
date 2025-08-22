import time
import sys
import subprocess
from app.main import app, db
from app.data.initialize_data import create_all_data

if __name__ == '__main__':
    # Wait for the database to be ready
    time.sleep(5)

    load_init = '--load-init' in sys.argv or '-i' in sys.argv
    load_demo = '--load-demo' in sys.argv or '-d' in sys.argv

    with app.app_context():
        # Run database migrations automatically
        try:
            subprocess.run(['flask', 'db', 'upgrade'], check=True)
            print("Database migrations applied successfully")
        except subprocess.CalledProcessError:
            print("Migration failed or no migrations to apply")
        except FileNotFoundError:
            print("Flask command not found - migrations may need to be run manually")
        
        if load_init:
            create_all_data()
        #if load_demo:
            #load_demo_data()

    # Start the Flask application
    app.run(host='0.0.0.0', port=4000)