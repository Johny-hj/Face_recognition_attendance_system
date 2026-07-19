"""
Configuration module for Face Recognition Attendance System.

Supports development and production environments via FLASK_ENV.
Loads environment variables from .env file using python-dotenv.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration with shared settings."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads'
    )
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    RECOGNITION_THRESHOLD = 0.6
    CAMERA_RESOLUTION = (640, 480)
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(Config):
    """Development configuration with SQLite default."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///attendance.db'
    )


class ProductionConfig(Config):
    """Production configuration for deployment on Render."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '')

    # Handle Render's postgres:// -> postgresql:// issue
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            'postgres://', 'postgresql://', 1
        )


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
