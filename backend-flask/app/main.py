from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore
from flask_jwt_extended import JWTManager
from datetime import timedelta
from .db import db
from .routes.lesson_routes import lesson_bp
from .routes.student_routes import student_bp
from .routes.curriculum_routes import curriculum_bp
from .routes.level_routes import level_bp
from .routes.unit_routes import unit_bp
from .routes.student_level_history_routes import student_level_history_bp
from .routes.lesson_student_routes import lesson_student_bp
from .routes.quiz_routes import quiz_bp
from .routes.student_lesson_quiz_routes import student_lesson_quiz_bp
from .routes.student_status_routes import student_status_bp
from .routes.student_status_history_routes import student_status_history_bp
from .routes.user_routes import user_bp
from .models.user_model import User
from .routes.authentication import auth_bp, refresh_expiring_jwts

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lesson_organizer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_PASSWORD_SALT'] = 'super-secret-salt'
app.config['JWT_SECRET_KEY'] = 'another-super-secret'

# Initialize JWT
app.config['JWT_VERIFY_SUB'] = False
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
app.config["JWT_COOKIE_SECURE"] = False # Set True in production

# Initialize Flask-Migrate
migrate = Migrate(app, db)

db.init_app(app)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, None)
security = Security(app, user_datastore)


jwt = JWTManager(app)

# Configure CORS
CORS(app, resources={r"/api/*": {"origins": "*", "supports_credentials": True}})

app.register_blueprint(lesson_bp, url_prefix='/api')
app.register_blueprint(student_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(curriculum_bp, url_prefix='/api')
app.register_blueprint(level_bp, url_prefix='/api')
app.register_blueprint(unit_bp, url_prefix='/api')
app.register_blueprint(student_level_history_bp, url_prefix='/api')
app.register_blueprint(lesson_student_bp, url_prefix='/api')
app.register_blueprint(quiz_bp, url_prefix='/api')
app.register_blueprint(student_lesson_quiz_bp, url_prefix='/api')
app.register_blueprint(student_status_bp, url_prefix='/api')
app.register_blueprint(student_status_history_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')

app.after_request(refresh_expiring_jwts)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=4000)