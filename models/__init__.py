"""
Models package for Face Recognition Attendance System.

Initializes the shared SQLAlchemy instance and imports all model classes
so they are registered with the ORM when this package is imported.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models so they are registered with SQLAlchemy
from models.student import Student  # noqa: E402, F401
from models.attendance import Attendance  # noqa: E402, F401
from models.admin import Admin  # noqa: E402, F401
from models.settings import Settings  # noqa: E402, F401
