from flask import Flask
from flask_cors import CORS
from flask_security import Security, SQLAlchemyUserDatastore
from flask_jwt_extended import JWTManager
from .db import db
from .routes.lessons import lessons_bp
from .routes.students import students_bp
from .models.user import User
from .routes.user import user_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lesson_organizer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_PASSWORD_SALT'] = 'super-secret-salt'
app.config['JWT_SECRET_KEY'] = 'another-super-secret'

db.init_app(app)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, None)
security = Security(app, user_datastore)

# Initialize JWT
jwt = JWTManager(app)

# Configure CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.register_blueprint(lessons_bp, url_prefix='/api')
app.register_blueprint(students_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=4000)