"""
Flask Application Factory
"""
import sys
import os
from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    # Ensure core dir is on path
    core_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if core_dir not in sys.path:
        sys.path.insert(0, core_dir)

    # --- Config ---
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///attendance.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-2026')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    app.config['UPLOAD_FOLDER'] = os.path.abspath(upload_dir)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # --- Extensions ---
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r'/api/*': {'origins': '*'}})

    # --- Blueprints ---
    from app.routes import auth_bp, attendance_bp, students_bp, classes_bp, reports_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(classes_bp)
    app.register_blueprint(reports_bp)

    # --- DB init + seed ---
    with app.app_context():
        from app.models import User, Student, Classroom, Attendance  # noqa: F401
        db.create_all()
        _seed_defaults()

    # --- Error handlers ---
    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Not found'}, 404

    @app.errorhandler(500)
    def server_error(e):
        return {'error': 'Internal server error'}, 500

    return app


def _seed_defaults():
    """Create default admin user and classroom on first run."""
    from app.models.user import User
    from app.models.classroom import Classroom

    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@school.local', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('[SEED] Created default admin  (admin / admin123)')

    if not Classroom.query.first():
        c = Classroom(name='CS-101', department='Computer Science', section='A')
        db.session.add(c)
        db.session.commit()
        print('[SEED] Created default classroom CS-101')
