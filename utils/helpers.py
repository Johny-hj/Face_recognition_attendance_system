"""
Helper utilities for Face Recognition Attendance System.

Provides file upload handling, validation, ID generation, and
query pagination helpers used across routes.
"""

import os
import re
from datetime import datetime

from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}


def allowed_file(filename):
    """Check if a filename has an allowed image extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, upload_folder, prefix=''):
    """Save an uploaded file with a secure, timestamped filename.

    Args:
        file: Werkzeug FileStorage object.
        upload_folder: Absolute path to the destination directory.
        prefix: Optional string prepended to the filename.

    Returns:
        The saved filename (relative), or None if the file is invalid.
    """
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if prefix:
            filename = f"{prefix}_{filename}"
        # Add timestamp to prevent filename collisions
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filename
    return None


def format_datetime(dt, fmt='%Y-%m-%d %H:%M:%S'):
    """Format a datetime object to a string, returning '' for None."""
    if dt:
        return dt.strftime(fmt)
    return ''


def validate_email(email):
    """Return True if *email* matches a basic email pattern, or if empty."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None if email else True


def validate_phone(phone):
    """Return True if *phone* matches a basic phone pattern, or if empty."""
    pattern = r'^[+]?[0-9\s-]{7,15}$'
    return re.match(pattern, phone) is not None if phone else True


def generate_student_id():
    """Generate the next sequential student ID (e.g. STU001, STU002, …).

    Queries the database for the highest existing student to determine
    the next number.
    """
    from models.student import Student

    last_student = Student.query.order_by(Student.id.desc()).first()
    if last_student:
        # Extract numeric portion from the last student_id
        num = int(last_student.student_id.replace('STU', '')) + 1
    else:
        num = 1
    return f'STU{num:03d}'


def paginate_query(query, page, per_page=10):
    """Paginate a SQLAlchemy query and return metadata alongside items.

    Returns:
        dict with keys: items, page, per_page, total, pages,
        has_prev, has_next, prev_num, next_num.
    """
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': pagination.items,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'total': pagination.total,
        'pages': pagination.pages,
        'has_prev': pagination.has_prev,
        'has_next': pagination.has_next,
        'prev_num': pagination.prev_num,
        'next_num': pagination.next_num,
    }
