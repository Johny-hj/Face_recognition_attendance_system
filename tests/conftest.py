"""
Pytest configuration and shared fixtures for the Face Recognition Attendance System.
"""
import pytest
import sys
import os

# Ensure the project root is on sys.path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db as _db


@pytest.fixture(scope='function')
def app():
    """Create an application instance configured for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SERVER_NAME'] = 'localhost'
    app.config['LOGIN_DISABLED'] = False

    with app.app_context():
        _db.create_all()

        # Seed a test admin user
        from models.admin import Admin
        admin = Admin(username='testadmin', email='test@test.com')
        admin.set_password('testpass')
        _db.session.add(admin)
        _db.session.commit()

        yield app

        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Provide a Flask test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def db(app):
    """Provide the SQLAlchemy database instance."""
    return _db


@pytest.fixture(scope='function')
def auth_client(client):
    """Provide a test client that is already logged in as the test admin."""
    client.post('/login', data={
        'username': 'testadmin',
        'password': 'testpass'
    }, follow_redirects=True)
    return client


@pytest.fixture(scope='function')
def sample_student(app, db):
    """Create and return a sample student for testing."""
    from models.student import Student
    student = Student(
        name='John Doe',
        roll_number='CS001',
        department='Computer Science',
        email='john@example.com'
    )
    db.session.add(student)
    db.session.commit()
    return student


@pytest.fixture(scope='function')
def sample_attendance(app, db, sample_student):
    """Create and return a sample attendance record for today."""
    from models.attendance import Attendance
    from datetime import date
    record = Attendance(
        student_id=sample_student.id,
        date=date.today(),
        status='present',
        confidence=95.5
    )
    db.session.add(record)
    db.session.commit()
    return record
