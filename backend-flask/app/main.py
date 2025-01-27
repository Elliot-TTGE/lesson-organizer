from flask import Flask
from flask_cors import CORS
from .db import db
from .routes.lessons import lessons_bp
from .routes.students import students_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lesson_organizer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
CORS(app)

app.register_blueprint(lessons_bp, url_prefix='/api')
app.register_blueprint(students_bp, url_prefix='/api')

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=4000)