"""Attendance routes — process photos, confirm, history."""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import date, datetime
import os, uuid

from app import db
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.classroom import Classroom
from app.services.core_wrapper import CoreFaceRecognitionService

attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')
core_service = CoreFaceRecognitionService()


@attendance_bp.route('/process', methods=['POST'])
@jwt_required()
def process_attendance():
    try:
        classroom_id = request.form.get('classroom_id')
        if not classroom_id:
            return {'error': 'classroom_id required'}, 400

        classroom = Classroom.query.get(int(classroom_id))
        if not classroom:
            return {'error': 'Classroom not found'}, 404

        photos = request.files.getlist('photos')
        if not photos or photos[0].filename == '':
            return {'error': 'No photos uploaded'}, 400

        # Save to temp
        upload_dir = current_app.config['UPLOAD_FOLDER']
        temp_files = []
        for photo in photos:
            ext = os.path.splitext(secure_filename(photo.filename))[1] or '.jpg'
            fname = f"{uuid.uuid4().hex}{ext}"
            fpath = os.path.join(upload_dir, fname)
            photo.save(fpath)
            temp_files.append(fpath)

        result = core_service.process_classroom_photos(temp_files, int(classroom_id))

        # Cleanup
        for fp in temp_files:
            if os.path.exists(fp):
                os.remove(fp)

        return jsonify(result), 200
    except Exception as exc:
        return {'error': str(exc)}, 500


@attendance_bp.route('/confirm', methods=['POST'])
@jwt_required()
def confirm_attendance():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        classroom_id = data.get('classroom_id')
        records = data.get('attendance', [])
        att_date_str = data.get('date')  # optional YYYY-MM-DD

        if not classroom_id or not records:
            return {'error': 'classroom_id and attendance list required'}, 400

        att_date = (datetime.strptime(att_date_str, '%Y-%m-%d').date()
                    if att_date_str else date.today())

        saved = 0
        for rec in records:
            roll = str(rec.get('student_id', rec.get('roll_number', '')))
            status = rec.get('status', 'absent')
            confidence = rec.get('confidence_score')
            match_type = rec.get('match_type')

            # Find or create student in SQL
            student = Student.query.filter_by(roll_number=roll).first()
            if not student:
                student = Student(roll_number=roll,
                                  name=rec.get('name', f'Student {roll}'))
                db.session.add(student)
                db.session.flush()

            existing = Attendance.query.filter_by(
                student_id=student.id,
                classroom_id=int(classroom_id),
                attendance_date=att_date
            ).first()

            if existing:
                existing.status = status
                existing.confidence_score = confidence
                existing.match_type = match_type
                existing.marked_by_id = user_id
            else:
                db.session.add(Attendance(
                    student_id=student.id,
                    classroom_id=int(classroom_id),
                    attendance_date=att_date,
                    status=status,
                    confidence_score=confidence,
                    match_type=match_type,
                    marked_by_id=user_id,
                ))
            saved += 1

        db.session.commit()
        return {'status': 'success', 'saved': saved}, 200
    except Exception as exc:
        db.session.rollback()
        return {'error': str(exc)}, 500


@attendance_bp.route('/history/<int:classroom_id>', methods=['GET'])
@jwt_required()
def attendance_history(classroom_id):
    try:
        classroom = Classroom.query.get(classroom_id)
        if not classroom:
            return {'error': 'Classroom not found'}, 404

        query = Attendance.query.filter_by(classroom_id=classroom_id)

        date_str = request.args.get('date')
        if date_str:
            query = query.filter_by(
                attendance_date=datetime.strptime(date_str, '%Y-%m-%d').date()
            )

        query = query.order_by(Attendance.attendance_date.desc())
        limit = request.args.get('limit', 200, type=int)
        rows = query.limit(limit).all()

        return {
            'classroom': classroom.to_dict(),
            'records': [r.to_dict() for r in rows],
        }, 200
    except Exception as exc:
        return {'error': str(exc)}, 500
