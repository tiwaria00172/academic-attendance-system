"""Attendance record model."""
from app import db


class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id'), nullable=False, index=True)
    attendance_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(10), nullable=False)          # 'present' | 'absent'
    confidence_score = db.Column(db.Float, nullable=True)
    match_type = db.Column(db.String(50), nullable=True)       # auto_marked, manual, etc.
    marked_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    marked_at = db.Column(db.DateTime, default=db.func.now())

    __table_args__ = (
        db.UniqueConstraint('student_id', 'classroom_id', 'attendance_date',
                            name='uq_student_class_date'),
    )

    marked_by = db.relationship('User', backref='marked_attendance')
    classroom = db.relationship('Classroom', backref='records')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else 'Unknown',
            'student_roll': self.student.roll_number if self.student else '',
            'classroom_id': self.classroom_id,
            'attendance_date': self.attendance_date.isoformat(),
            'status': self.status,
            'confidence_score': self.confidence_score,
            'match_type': self.match_type,
        }
