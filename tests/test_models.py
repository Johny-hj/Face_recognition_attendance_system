import pytest
from models.student import Student
from models.attendance import Attendance
from models.admin import Admin
from models.settings import Settings
from datetime import date, time

def test_admin_password(app, db):
    with app.app_context():
        admin = Admin(username='admin2', email='admin2@example.com')
        admin.set_password('mysecurepassword')
        db.session.add(admin)
        db.session.commit()
        
        assert admin.check_password('mysecurepassword') is True
        assert admin.check_password('wrongpassword') is False

def test_student_creation(app, db):
    with app.app_context():
        student = Student(
            student_id='STU001',
            name='John Doe',
            roll_number='CS001',
            department='Computer Science'
        )
        db.session.add(student)
        db.session.commit()
        
        saved = Student.query.filter_by(student_id='STU001').first()
        assert saved is not None
        assert saved.name == 'John Doe'
        assert saved.to_dict()['student_id'] == 'STU001'

def test_attendance_creation(app, db):
    with app.app_context():
        student = Student(student_id='STU002', name='Jane Doe', roll_number='CS002', department='CS')
        db.session.add(student)
        db.session.commit()
        
        att = Attendance(
            student_id=student.id,
            date=date(2023, 10, 1),
            time=time(9, 0),
            status='Present',
            confidence=0.95
        )
        db.session.add(att)
        db.session.commit()
        
        saved = Attendance.query.filter_by(student_id=student.id).first()
        assert saved is not None
        assert saved.status == 'Present'

def test_settings(app, db):
    with app.app_context():
        Settings.set('test_key', 'test_value')
        assert Settings.get('test_key') == 'test_value'
        assert Settings.get('non_existent', 'default') == 'default'
