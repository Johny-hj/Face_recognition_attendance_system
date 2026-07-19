"""
Attendance Routes.

Provides attendance listing, live camera recognition, face recognition API,
video streaming, and data export/download endpoints.
"""

from datetime import date, datetime
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, jsonify, Response, send_file, current_app
)
from flask_login import login_required
from services.recognition_service import RecognitionService
from services.attendance_service import AttendanceService
from services.camera_service import CameraService
from services.export_service import ExportService
from services.student_service import StudentService
from models.settings import Settings

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')


@attendance_bp.route('/')
@login_required
def index():
    """List attendance records with date, department, and student filters."""
    try:
        target_date = request.args.get('date', '')
        department = request.args.get('department', '').strip()
        student_name = request.args.get('student', '').strip()
        page = request.args.get('page', 1, type=int)

        start_date = None
        end_date = None

        if target_date:
            try:
                start_date = datetime.strptime(target_date, '%Y-%m-%d').date()
                end_date = start_date
            except ValueError:
                flash('Invalid date format. Use YYYY-MM-DD.', 'error')

        pagination = AttendanceService.get_filtered_attendance(
            department=department if department else None,
            student_name=student_name if student_name else None,
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=20
        )

        departments = StudentService.get_departments()

        status = request.args.get('status', '').strip()

        filters = {
            'date': target_date,
            'department': department,
            'status': status,
            'student': student_name
        }

        return render_template(
            'attendance/index.html',
            attendance_records=pagination,
            departments=departments,
            filters=filters,
            page=page,
            total_pages=pagination.pages
        )
    except Exception as e:
        flash(f'Error loading attendance records: {str(e)}', 'error')
        # Create a fake empty pagination object
        class EmptyPagination:
            items = []
            page = 1
            per_page = 20
            pages = 1
            total = 0
            has_prev = False
            has_next = False
            prev_num = None
            next_num = None
        return render_template(
            'attendance/index.html',
            attendance_records=EmptyPagination(),
            departments=[],
            filters={'date': '', 'department': '', 'status': '', 'student': ''},
            page=1,
            total_pages=1
        )


@attendance_bp.route('/start')
@login_required
def start():
    """Render the live camera recognition page."""
    try:
        threshold = Settings.get('recognition_threshold', '0.6')
        return render_template(
            'attendance/camera.html',
            threshold=float(threshold)
        )
    except Exception as e:
        flash(f'Error starting attendance: {str(e)}', 'error')
        return redirect(url_for('attendance.index'))


@attendance_bp.route('/recognize', methods=['POST'])
@login_required
def recognize():
    """JSON API for face recognition from a base64-encoded frame.

    Accepts JSON body with 'frame' key containing a base64 JPEG string.
    Detects faces, matches against known encodings, and marks attendance
    for recognized students.

    Returns JSON with list of recognition results.
    """
    try:
        data = request.get_json()
        if not data or 'frame' not in data:
            return jsonify({
                'success': False,
                'message': 'No frame data provided.'
            }), 400

        frame_data = data['frame']

        # Strip data URL prefix if present
        if ',' in frame_data:
            frame_data = frame_data.split(',', 1)[1]

        # Decode base64 frame to numpy array
        frame = CameraService.base64_to_frame(frame_data)
        if frame is None:
            return jsonify({
                'success': False,
                'message': 'Failed to decode frame.'
            }), 400

        # Get recognition threshold from settings or request
        threshold = float(
            data.get('threshold',
                      Settings.get('recognition_threshold', '0.6'))
        )

        # Run face recognition
        faces = RecognitionService.recognize_faces(frame, tolerance=threshold)

        results = []
        for face in faces:
            top, right, bottom, left = face['location']
            result = {
                'confidence': round(face['confidence'] * 100, 1),
                'location': [top, right, bottom, left],
                'known': face['known']
            }

            if face['known'] and face['student']:
                student = face['student']
                # Mark attendance for recognized student
                attendance, status = AttendanceService.mark_attendance(
                    student_id=student.id,
                    confidence=face['confidence']
                )

                result['name'] = student.name
                result['roll_number'] = student.roll_number
                result['department'] = student.department
                result['student_id'] = student.student_id
                result['status'] = status
                result['attendance_status'] = attendance.status
            else:
                result['name'] = 'Unknown'
                result['roll_number'] = ''
                result['department'] = ''
                result['student_id'] = ''
                result['status'] = 'unknown'
                result['attendance_status'] = ''

            results.append(result)

        return jsonify({
            'success': True,
            'faces': results,
            'count': len(results)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Recognition error: {str(e)}'
        }), 500


@attendance_bp.route('/video-feed')
@login_required
def video_feed():
    """Streaming endpoint for server-side camera MJPEG feed."""
    try:
        return Response(
            CameraService.generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Camera error: {str(e)}'
        }), 500


@attendance_bp.route('/export')
@login_required
def export():
    """Export attendance data as Excel or CSV file.

    Query params:
        type: 'today', 'weekly', 'monthly', or 'custom'
        start_date: Start date for custom range (YYYY-MM-DD)
        end_date: End date for custom range (YYYY-MM-DD)
        department: Optional department filter
        format: 'excel' or 'csv' (default: 'excel')
    """
    try:
        export_type = request.args.get('type', 'today')
        department = request.args.get('department', '').strip() or None
        export_format = request.args.get('format', 'excel')

        today = date.today()

        if export_type == 'today':
            start_date = today
            end_date = today
            filename_suffix = today.strftime('%Y_%m_%d')
        elif export_type == 'weekly':
            from datetime import timedelta
            start_date = today - timedelta(days=today.weekday())
            end_date = today
            filename_suffix = f'week_{today.strftime("%Y_%m_%d")}'
        elif export_type == 'monthly':
            start_date = today.replace(day=1)
            end_date = today
            filename_suffix = today.strftime('%Y_%m')
        elif export_type == 'custom':
            start_str = request.args.get('start_date', '')
            end_str = request.args.get('end_date', '')
            if not start_str or not end_str:
                flash('Start date and end date are required for custom export.', 'error')
                return redirect(url_for('attendance.index'))
            try:
                start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format. Use YYYY-MM-DD.', 'error')
                return redirect(url_for('attendance.index'))
            filename_suffix = f'{start_date.strftime("%Y_%m_%d")}_to_{end_date.strftime("%Y_%m_%d")}'
        else:
            flash('Invalid export type.', 'error')
            return redirect(url_for('attendance.index'))

        if export_format == 'csv':
            buffer = ExportService.export_csv(start_date, end_date, department)
            filename = f'attendance_{filename_suffix}.csv'
            mimetype = 'text/csv'
        else:
            buffer = ExportService.export_excel(start_date, end_date, department)
            filename = f'attendance_{filename_suffix}.xlsx'
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )

    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'error')
        return redirect(url_for('attendance.index'))


@attendance_bp.route('/download')
@login_required
def download():
    """Quick download of today's attendance as an Excel file."""
    try:
        buffer = ExportService.export_today()
        today = date.today()
        filename = f'attendance_{today.strftime("%Y_%m_%d")}.xlsx'
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        flash(f'Error downloading attendance: {str(e)}', 'error')
        return redirect(url_for('attendance.index'))
