"""Authentication routes — login, signup, current user."""
from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/seed', methods=['POST', 'GET'])
def seed():
    """Auto-create default admin, teacher, and student accounts."""
    from app.models.student import Student
    created = []
    defaults = [
        ('admin', 'admin@school.edu', 'admin123', 'admin'),
        ('teacher', 'teacher@school.edu', 'teacher123', 'teacher'),
        ('student', 'student@school.edu', 'student123', 'student')
    ]
    for username, email, pw, role in defaults:
        if not User.query.filter_by(username=username).first():
            u = User(username=username, email=email, role=role)
            u.set_password(pw)
            db.session.add(u)
            created.append(username)
        if role == 'student' and not Student.query.filter((Student.roll_number == username) | (Student.email == email)).first():
            s = Student(roll_number=username, name="Default Student", email=email, department="Computer Science", is_active=True)
            db.session.add(s)
    db.session.commit()
    return {'message': 'Seed completed', 'created': created}, 200


@auth_bp.route('/signup', methods=['POST'])
def signup():
    from app.models.student import Student
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'teacher').strip().lower()
    if role not in ['admin', 'teacher', 'student']:
        role = 'teacher'

    if not username or not email or not password:
        return {'error': 'username, email and password required'}, 400
    if User.query.filter((User.username.ilike(username)) | (User.email.ilike(email))).first():
        return {'error': 'Username or email already registered'}, 409

    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)

    if role == 'student':
        existing_student = Student.query.filter((Student.roll_number == username) | (Student.email == email)).first()
        if not existing_student:
            new_student = Student(
                roll_number=username,
                name=username.replace('_', ' ').title(),
                email=email,
                department="Computer Science",
                is_active=True
            )
            db.session.add(new_student)

    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return {'access_token': token, 'user': user.to_dict()}, 201


@auth_bp.route('/login', methods=['POST'])
def login():
    from app.models.student import Student
    # Auto-seed default accounts if database has no users
    if User.query.count() == 0:
        seed()
    elif not User.query.filter_by(username='admin').first():
        seed()

    data = request.get_json() or {}
    raw_user = data.get('username', '').strip()
    password = data.get('password', '')

    user = User.query.filter((User.username.ilike(raw_user)) | (User.email.ilike(raw_user))).first()
    if not user or not user.check_password(password):
        return {'error': 'Invalid credentials. Please check username/email and password.'}, 401

    if user.role == 'student':
        existing_student = Student.query.filter((Student.roll_number == user.username) | (Student.email == user.email)).first()
        if not existing_student:
            new_student = Student(
                roll_number=user.username,
                name=user.username.replace('_', ' ').title(),
                email=user.email,
                department="Computer Science",
                is_active=True
            )
            db.session.add(new_student)
            db.session.commit()

    token = create_access_token(identity=str(user.id))
    return {'access_token': token, 'user': user.to_dict()}, 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return {'error': 'User not found'}, 404
    return {'user': user.to_dict()}, 200
