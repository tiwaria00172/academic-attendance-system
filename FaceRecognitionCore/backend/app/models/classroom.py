"""Classroom model with student enrollment."""
from app import db

# Many-to-many enrollment table
enrollment = db.Table(
    'enrollment',
    db.Column('student_id', db.Integer, db.ForeignKey('students.id'), primary_key=True),
    db.Column('classroom_id', db.Integer, db.ForeignKey('classrooms.id'), primary_key=True),
)


class Classroom(db.Model):
    __tablename__ = 'classrooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=True)
    section = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

    students = db.relationship('Student', secondary=enrollment,
                               backref=db.backref('classrooms', lazy=True), lazy=True)

    def to_dict(self, include_students=False):
        d = {
            'id': self.id,
            'name': self.name,
            'department': self.department,
            'section': self.section,
            'student_count': len(self.students),
            'is_active': self.is_active,
        }
        if include_students:
            d['students'] = [s.to_dict() for s in self.students]
        return d
