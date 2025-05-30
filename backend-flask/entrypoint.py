import time
import sys
from app.main import app, db
from app.data.load_demo_data import load_demo_data

if __name__ == '__main__':
    # Wait for the database to be ready
    time.sleep(5)

    load_demo = '--load-demo' in sys.argv or '-d' in sys.argv

    with app.app_context():
        db.create_all()
        if load_demo:
            load_demo_data()

    # Start the Flask application
    app.run(host='0.0.0.0', port=4000)