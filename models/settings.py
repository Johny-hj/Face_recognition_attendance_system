"""
Settings model for Face Recognition Attendance System.

Provides a key-value store for application settings with
class-level get/set helpers and default seeding.
"""

from models import db


class Settings(db.Model):
    """Key-value store for application-wide settings."""

    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))

    @classmethod
    def get(cls, key, default=None):
        """Retrieve a setting value by key, returning *default* if not found."""
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default

    @classmethod
    def set(cls, key, value, description=None):
        """Create or update a setting."""
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
        else:
            setting = cls(key=key, value=str(value), description=description)
            db.session.add(setting)
        db.session.commit()

    @classmethod
    def seed_defaults(cls):
        """Insert default settings if they do not already exist."""
        defaults = {
            'recognition_threshold': (
                '0.6',
                'Face recognition tolerance (lower = stricter)',
            ),
            'camera_resolution': ('640x480', 'Camera resolution WxH'),
            'attendance_time_format': ('24h', 'Time format: 12h or 24h'),
            'theme': ('light', 'UI theme: light or dark'),
        }
        for key, (value, desc) in defaults.items():
            if not cls.query.filter_by(key=key).first():
                db.session.add(cls(key=key, value=value, description=desc))
        db.session.commit()

    def __repr__(self):
        return f'<Settings {self.key}={self.value}>'
