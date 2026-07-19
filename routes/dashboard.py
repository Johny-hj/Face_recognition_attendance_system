"""
Dashboard Routes.

Provides the main dashboard view with attendance statistics
and a JSON API endpoint for AJAX stat refreshes.
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from services.attendance_service import AttendanceService

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    """Render the main dashboard with statistics and recent attendance."""
    try:
        stats = AttendanceService.get_stats()
        recent = AttendanceService.get_recent_attendance()
        return render_template(
            'dashboard.html',
            stats=stats,
            recent=recent
        )
    except Exception as e:
        return render_template(
            'dashboard.html',
            stats={
                'total_students': 0,
                'today_present': 0,
                'today_absent': 0,
                'today_late': 0,
                'recognition_rate': 0,
                'week_data': [],
                'dept_data': [],
            },
            recent=[],
            error=str(e)
        )


@dashboard_bp.route('/stats')
@login_required
def stats():
    """JSON API endpoint returning dashboard statistics for AJAX refresh."""
    try:
        stats = AttendanceService.get_stats()
        recent = AttendanceService.get_recent_attendance(limit=5)
        recent_data = []
        for r in recent:
            recent_data.append({
                'id': r.id,
                'student_name': r.student.name if r.student else 'Unknown',
                'roll_number': r.student.roll_number if r.student else '',
                'department': r.student.department if r.student else '',
                'date': r.date.strftime('%Y-%m-%d'),
                'time': r.time.strftime('%H:%M:%S') if r.time else '',
                'status': r.status,
                'confidence': round(r.confidence * 100, 1) if r.confidence else 0
            })
        return jsonify({
            'success': True,
            'stats': stats,
            'recent': recent_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
