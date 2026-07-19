"""
Routes package for Face Recognition Attendance System.

Contains Flask Blueprint definitions for main, dashboard, students,
attendance, reports, and settings routes.
"""

from routes.main import main_bp
from routes.dashboard import dashboard_bp
from routes.students import students_bp
from routes.attendance import attendance_bp
from routes.reports import reports_bp
from routes.settings import settings_bp
