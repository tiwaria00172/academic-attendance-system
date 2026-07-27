"""Student model - student records with optional face encoding."""
from app import db
import json
import numpy as np


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    face_encoding_json = db.Column(db.Text, nullable=True)
    has_face_data = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    attendance_records = db.relationship('Attendance', backref='student', lazy=True)

    def set_face_encoding(self, encoding):
        if isinstance(encoding, np.ndarray):
            encoding = encoding.tolist()
        self.face_encoding_json = json.dumps(encoding)
        self.has_face_data = True

    def get_face_encoding(self):
        if not self.face_encoding_json:
            return None
        return np.array(json.loads(self.face_encoding_json), dtype=np.float64)

    def to_dict(self):
        return {
            'id': self.id,
            'roll_number': self.roll_number,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'has_face_data': self.has_face_data,
            'is_active': self.is_active,
        }
