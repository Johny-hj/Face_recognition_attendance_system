"""
Settings Routes.

Provides viewing and updating application settings
such as recognition threshold, camera resolution, and theme.
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash
)
from flask_login import login_required
from models.settings import Settings

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


@settings_bp.route('/', methods=['GET'])
@login_required
def index():
    """Render the settings page with current configuration values."""
    try:
        settings = {
            'recognition_threshold': Settings.get('recognition_threshold', '0.6'),
            'detection_model': Settings.get('detection_model', 'hog'),
            'camera_resolution': Settings.get('camera_resolution', '640x480'),
            'capture_interval': Settings.get('capture_interval', '3'),
            'late_threshold': Settings.get('late_threshold', '15'),
            'attendance_start_time': Settings.get('attendance_start_time', '09:00'),
            'attendance_time_format': Settings.get('attendance_time_format', '24h'),
            'theme': Settings.get('theme', 'dark'),
            'records_per_page': int(Settings.get('records_per_page', '25')),
        }
        return render_template('settings.html', settings=settings)
    except Exception as e:
        flash(f'Error loading settings: {str(e)}', 'error')
        return render_template('settings.html', settings={
            'recognition_threshold': '0.6',
            'detection_model': 'hog',
            'camera_resolution': '640x480',
            'capture_interval': '3',
            'late_threshold': '15',
            'attendance_start_time': '09:00',
            'attendance_time_format': '24h',
            'theme': 'dark',
            'records_per_page': 25,
        })


@settings_bp.route('/', methods=['POST'])
@login_required
def update():
    """Update application settings from form data."""
    try:
        # Recognition threshold validation
        threshold = request.form.get('recognition_threshold', '').strip()
        if threshold:
            try:
                threshold_val = float(threshold)
                if not (0.0 <= threshold_val <= 1.0):
                    flash(
                        'Recognition threshold must be between 0.0 and 1.0.',
                        'error'
                    )
                    return redirect(url_for('settings.index'))
                Settings.set(
                    'recognition_threshold',
                    str(threshold_val),
                    'Face recognition distance threshold (0.0-1.0, lower is stricter)'
                )
            except ValueError:
                flash('Invalid recognition threshold value.', 'error')
                return redirect(url_for('settings.index'))

        # Camera resolution validation
        camera_resolution = request.form.get('camera_resolution', '').strip()
        if camera_resolution:
            valid_resolutions = [
                '320x240', '640x480', '800x600',
                '1024x768', '1280x720', '1920x1080'
            ]
            if camera_resolution not in valid_resolutions:
                flash(
                    f'Invalid camera resolution. Choose from: '
                    f'{", ".join(valid_resolutions)}',
                    'error'
                )
                return redirect(url_for('settings.index'))
            Settings.set(
                'camera_resolution',
                camera_resolution,
                'Camera capture resolution (WxH)'
            )

        # Attendance time format
        time_format = request.form.get('attendance_time_format', '').strip()
        if time_format:
            valid_formats = ['12h', '24h']
            if time_format not in valid_formats:
                flash('Invalid time format. Choose 12h or 24h.', 'error')
                return redirect(url_for('settings.index'))
            Settings.set(
                'attendance_time_format',
                time_format,
                'Time display format for attendance records'
            )

        theme = request.form.get('theme', '').strip()
        if theme:
            valid_themes = ['light', 'dark', 'auto']
            if theme not in valid_themes:
                flash('Invalid theme. Choose light, dark, or auto.', 'error')
                return redirect(url_for('settings.index'))
            Settings.set('theme', theme, 'Application UI theme')

        # Additional fields
        detection_model = request.form.get('detection_model', '').strip()
        if detection_model:
            Settings.set('detection_model', detection_model, 'Face detection model')

        capture_interval = request.form.get('capture_interval', '').strip()
        if capture_interval:
            Settings.set('capture_interval', capture_interval, 'Camera capture interval in seconds')

        late_threshold = request.form.get('late_threshold', '').strip()
        if late_threshold:
            Settings.set('late_threshold', late_threshold, 'Minutes after start time to mark as Late')

        attendance_start_time = request.form.get('attendance_start_time', '').strip()
        if attendance_start_time:
            Settings.set('attendance_start_time', attendance_start_time, 'Default start time for attendance')

        records_per_page = request.form.get('records_per_page', '').strip()
        if records_per_page:
            Settings.set('records_per_page', records_per_page, 'Number of records per page')

        flash('Settings updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating settings: {str(e)}', 'error')

    return redirect(url_for('settings.index'))
