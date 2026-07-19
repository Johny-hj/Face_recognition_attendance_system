"""
Attendance model for Face Recognition Attendance System.

Records each attendance event with date, time, status, and
the face recognition confidence score.
"""

from datetime import date, datetime

from models import db


class Attendance(db.Model):
    """Represents a single attendance record for a student on a given date."""

    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey('students.id'), nullable=False
    )
    date = db.Column(db.Date, nullable=False, default=date.today)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='Present')  # Present, Absent, Late
    confidence = db.Column(db.Float)  # Recognition confidence 0-1
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint: one attendance per student per day
    __table_args__ = (
        db.UniqueConstraint('student_id', 'date', name='unique_student_date'),
    )

    def to_dict(self):
        """Serialize attendance record to a dictionary for JSON responses."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'roll_number': self.student.roll_number if self.student else None,
            'department': self.student.department if self.student else None,
            'date': self.date.isoformat() if self.date else None,
            'time': self.time.strftime('%H:%M:%S') if self.time else None,
            'status': self.status,
            'confidence': round(self.confidence * 100, 1) if self.confidence else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Attendance {self.student_id} on {self.date}>'
