"""
Custom decorators for Face Recognition Attendance System.

Provides access-control decorators for route protection.
"""

from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """Decorator that redirects unauthenticated users to the login page."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)

    return decorated_function
