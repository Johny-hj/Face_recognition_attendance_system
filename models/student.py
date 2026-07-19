"""
Student model for Face Recognition Attendance System.

Stores student information including photo path and face encoding
(pickled numpy array) for recognition.
"""

from datetime import datetime

from models import db


class Student(db.Model):
    """Represents a student enrolled in the attendance system."""

    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)  # e.g. STU001
    name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(10))  # 1st, 2nd, 3rd, 4th
    section = db.Column(db.String(10))  # A, B, C
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    photo = db.Column(db.String(255))  # path to photo file
    face_encoding = db.Column(db.LargeBinary)  # pickled numpy array
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to attendance records — cascade delete
    attendances = db.relationship(
        'Attendance', backref='student', lazy=True, cascade='all, delete-orphan'
    )

    def to_dict(self):
        """Serialize student to a dictionary for JSON responses."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'roll_number': self.roll_number,
            'department': self.department,
            'year': self.year,
            'section': self.section,
            'email': self.email,
            'phone': self.phone,
            'photo': self.photo,
            'has_face_encoding': self.face_encoding is not None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Student {self.student_id}: {self.name}>'
