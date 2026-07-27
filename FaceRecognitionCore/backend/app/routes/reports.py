"""Attendance reports and statistics."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from sqlalchemy import func

from app import db
from app.models.attendance import Attendance
from app.models.student import Student
from app.models.classroom import Classroom

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')


@reports_bp.route('/summary/<int:classroom_id>', methods=['GET'])
@jwt_required()
def class_summary(classroom_id):
    """Overall attendance stats for a classroom."""
    classroom = Classroom.query.get_or_404(classroom_id)

    total = Attendance.query.filter_by(classroom_id=classroom_id).count()
    present = Attendance.query.filter_by(
        classroom_id=classroom_id, status='present').count()
    absent = total - present

    unique_dates = db.session.query(
        func.count(func.distinct(Attendance.attendance_date))
    ).filter_by(classroom_id=classroom_id).scalar() or 0

    return {
        'classroom': classroom.to_dict(),
        'total_records': total,
        'present': present,
        'absent': absent,
        'attendance_rate': round(present / total * 100, 1) if total else 0,
        'sessions_held': unique_dates,
    }, 200


@reports_bp.route('/student/<int:student_id>', methods=['GET'])
@jwt_required()
def student_report(student_id):
    """Attendance report for a single student."""
    student = Student.query.get_or_404(student_id)

    records = Attendance.query.filter_by(student_id=student_id)\
        .order_by(Attendance.attendance_date.desc()).limit(100).all()

    total = len(records)
    present = sum(1 for r in records if r.status == 'present')

    return {
        'student': student.to_dict(),
        'total_sessions': total,
        'present': present,
        'absent': total - present,
        'attendance_rate': round(present / total * 100, 1) if total else 0,
        'records': [r.to_dict() for r in records],
    }, 200


@reports_bp.route('/daily/<int:classroom_id>', methods=['GET'])
@jwt_required()
def daily_report(classroom_id):
    """Per-date breakdown for the last 30 days."""
    classroom = Classroom.query.get_or_404(classroom_id)
    since = datetime.utcnow().date() - timedelta(days=30)

    rows = db.session.query(
        Attendance.attendance_date,
        Attendance.status,
        func.count(Attendance.id)
    ).filter(
        Attendance.classroom_id == classroom_id,
        Attendance.attendance_date >= since
    ).group_by(
        Attendance.attendance_date, Attendance.status
    ).all()

    # Aggregate
    days = {}
    for dt, status, cnt in rows:
        key = dt.isoformat()
        if key not in days:
            days[key] = {'date': key, 'present': 0, 'absent': 0}
        days[key][status] = cnt

    return {
        'classroom': classroom.to_dict(),
        'daily': sorted(days.values(), key=lambda x: x['date'], reverse=True),
    }, 200


@reports_bp.route('/export/<int:classroom_id>', methods=['GET'])
@jwt_required()
def export_csv(classroom_id):
    """Export attendance spreadsheet as a CSV file."""
    from flask import Response
    import csv
    import io

    classroom = Classroom.query.get_or_404(classroom_id)
    records = Attendance.query.filter_by(classroom_id=classroom_id)\
        .order_by(Attendance.attendance_date.desc(), Attendance.id.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Roll Number', 'Student Name', 'Department', 'Attendance Status', 'Date', 'Confidence Score', 'Verified By', 'Remarks'])

    for r in records:
        s = r.student
        writer.writerow([
            s.roll_number if s else 'N/A',
            s.name if s else 'Unknown Student',
            s.department if s else 'General',
            r.status.upper(),
            r.attendance_date.strftime('%Y-%m-%d'),
            f"{round(r.confidence_score * 100, 1)}%" if r.confidence_score else "N/A",
            r.verified_by or 'AI Auto-Verified',
            r.remarks or ''
        ])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=attendance_class_{classroom_id}_{datetime.utcnow().strftime("%Y%m%d")}.csv'}
    )
