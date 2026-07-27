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
    db.session.commit()
    return {'message': 'Seed completed', 'created': created}, 200


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'teacher').strip().lower()
    if role not in ['admin', 'teacher', 'student']:
        role = 'teacher'

    if not username or not email or not password:
        return {'error': 'username, email and password required'}, 400
    if User.query.filter_by(username=username).first():
        return {'error': 'Username already taken'}, 409

    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return {'access_token': token, 'user': user.to_dict()}, 201


@auth_bp.route('/login', methods=['POST'])
def login():
    # Auto-seed default accounts if database has no users
    if User.query.count() == 0:
        seed()
    elif not User.query.filter_by(username='admin').first():
        seed()

    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return {'error': 'Invalid credentials'}, 401

    token = create_access_token(identity=str(user.id))
    return {'access_token': token, 'user': user.to_dict()}, 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return {'error': 'User not found'}, 404
    return {'user': user.to_dict()}, 200
