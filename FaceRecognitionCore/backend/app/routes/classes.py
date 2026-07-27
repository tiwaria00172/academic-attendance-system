"""Classroom management routes."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app import db
from app.models.classroom import Classroom
from app.models.student import Student

classes_bp = Blueprint('classes', __name__, url_prefix='/api/classes')


@classes_bp.route('', methods=['GET'])
@jwt_required()
def list_classes():
    rooms = Classroom.query.filter_by(is_active=True).all()
    return {'classrooms': [c.to_dict() for c in rooms]}, 200


@classes_bp.route('/<int:cid>', methods=['GET'])
@jwt_required()
def get_class(cid):
    c = Classroom.query.get_or_404(cid)
    return {'classroom': c.to_dict(include_students=True)}, 200


@classes_bp.route('', methods=['POST'])
@jwt_required()
def create_class():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    if not name:
        return {'error': 'name required'}, 400
    if Classroom.query.filter_by(name=name).first():
        return {'error': 'Classroom name exists'}, 409

    c = Classroom(name=name, department=data.get('department'),
                  section=data.get('section'))
    db.session.add(c)
    db.session.commit()
    return {'classroom': c.to_dict()}, 201


@classes_bp.route('/<int:cid>/enroll', methods=['POST'])
@jwt_required()
def enroll_students(cid):
    classroom = Classroom.query.get_or_404(cid)
    data = request.get_json() or {}
    ids = data.get('student_ids', [])
    added = 0
    for sid in ids:
        student = Student.query.get(sid)
        if student and student not in classroom.students:
            classroom.students.append(student)
            added += 1
    db.session.commit()
    return {'enrolled': added, 'classroom': classroom.to_dict()}, 200
