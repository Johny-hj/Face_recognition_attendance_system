"""
Admin model for Face Recognition Attendance System.

Provides authentication via Flask-Login's UserMixin with
Werkzeug password hashing for secure credential storage.
"""

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from models import db


class Admin(UserMixin, db.Model):
    """Represents an administrator who can access the system."""

    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hash and store the password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify a password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Admin {self.username}>'
