"""
Gunicorn configuration for Face Recognition Attendance System.

Uses fewer workers and a longer timeout to accommodate the
memory-intensive face_recognition library.
"""

import os

bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
workers = 2  # Keep low for face recognition memory usage
timeout = 120  # Face recognition can be slow
accesslog = '-'
errorlog = '-'
loglevel = 'info'
