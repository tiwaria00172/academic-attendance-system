"""Student management routes."""
from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
import os, shutil

from app import db
from app.models.student import Student
from app.services.core_wrapper import CoreFaceRecognitionService
from config import Config

students_bp = Blueprint('students', __name__, url_prefix='/api/students')
core_service = CoreFaceRecognitionService()


@students_bp.route('', methods=['GET'])
@jwt_required()
def list_students():
    students = Student.query.filter_by(is_active=True).all()
    return {'students': [s.to_dict() for s in students]}, 200


@students_bp.route('/<int:sid>', methods=['GET'])
@jwt_required()
def get_student(sid):
    s = Student.query.get_or_404(sid)
    return {'student': s.to_dict()}, 200


@students_bp.route('', methods=['POST'])
@jwt_required()
def create_student():
    data = request.get_json() or {}
    roll = data.get('roll_number', '').strip()
    name = data.get('name', '').strip()
    if not roll or not name:
        return {'error': 'roll_number and name required'}, 400
    if Student.query.filter_by(roll_number=roll).first():
        return {'error': 'Roll number exists'}, 409

    s = Student(roll_number=roll, name=name,
                email=data.get('email'), phone=data.get('phone'),
                department=data.get('department'))
    db.session.add(s)
    db.session.commit()
    return {'student': s.to_dict()}, 201


@students_bp.route('/<int:sid>/photo', methods=['POST'])
@jwt_required()
def upload_photo(sid):
    """Upload a reference photo, extract encoding, copy to training dir."""
    student = Student.query.get_or_404(sid)
    if 'photo' not in request.files:
        return {'error': 'No photo file'}, 400

    photo = request.files['photo']
    filename = secure_filename(f"student_{student.roll_number}_{student.name}.jpg")

    # Save to training dir
    training_dir = Config.TRAINING_DATA_DIR
    os.makedirs(training_dir, exist_ok=True)
    dest = os.path.join(training_dir, filename)
    photo.save(dest)

    # Extract encoding via core
    encoding = core_service.extract_single_encoding(dest)
    if encoding is not None:
        student.set_face_encoding(encoding)
        db.session.commit()
        core_service.reload_database()
        return {'message': 'Photo uploaded, face registered', 'student': student.to_dict()}, 200

    return {'error': 'Could not extract face from photo'}, 422


@students_bp.route('/<int:sid>/photo_angles', methods=['POST'])
@jwt_required()
def upload_photo_angles(sid):
    """Upload 3 angles (front, left, right) for robust real-world enrollment."""
    student = Student.query.get_or_404(sid)
    files = request.files
    
    if not files:
        return {'error': 'No photo files provided'}, 400

    training_dir = Config.TRAINING_DATA_DIR
    os.makedirs(training_dir, exist_ok=True)
    
    encodings = []
    saved_angles = []
    
    for angle in ['front', 'left', 'right']:
        if angle in files and files[angle].filename:
            photo = files[angle]
            filename = secure_filename(f"student_{student.roll_number}_{student.name}_{angle}.jpg")
            dest = os.path.join(training_dir, filename)
            photo.save(dest)
            
            enc = core_service.extract_single_encoding(dest)
            if enc is not None:
                encodings.append(enc)
                saved_angles.append(angle)

    if not encodings:
        return {'error': 'Could not detect faces in any of the 3 angle photos. Ensure good lighting and clear view.'}, 422

    # Average the encodings across detected angles for a unified multi-angle vector
    import numpy as np
    avg_encoding = np.mean(encodings, axis=0)
    
    student.set_face_encoding(avg_encoding)
    db.session.commit()
    core_service.reload_database()
    
    return {
        'message': f'Successfully enrolled {len(saved_angles)} angles ({", ".join(saved_angles)}). Multi-angle AI profile active!',
        'angles_enrolled': saved_angles,
        'student': student.to_dict()
    }, 200


@students_bp.route('/sync', methods=['POST'])
@jwt_required()
def sync_from_core():
    """Sync core training-folder students into SQL database."""
    core_service.reload_database()
    sdb = core_service.student_database
    created = 0
    for sid, info in sdb.items():
        if not Student.query.filter_by(roll_number=str(sid)).first():
            s = Student(roll_number=str(sid), name=info['name'])
            s.set_face_encoding(info['encoding'])
            db.session.add(s)
            created += 1
    db.session.commit()
    return {'synced': created, 'total_core': len(sdb)}, 200
