"""
Reports Routes.

Provides filtered attendance reporting with pagination
and export functionality for Excel and CSV downloads.
"""

from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, send_file
)
from flask_login import login_required
from services.attendance_service import AttendanceService
from services.student_service import StudentService
from services.export_service import ExportService

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/')
@login_required
def index():
    """Render the reports page with filtered and paginated attendance data.

    Query params:
        start_date: Filter records on or after this date (YYYY-MM-DD).
        end_date: Filter records on or before this date (YYYY-MM-DD).
        department: Filter by student department.
        student_name: Filter by student name (partial match).
        page: Page number for pagination.
    """
    try:
        start_date_str = request.args.get('start_date', '').strip()
        end_date_str = request.args.get('end_date', '').strip()
        department = request.args.get('department', '').strip()
        student_name = request.args.get('student_name', '').strip()
        page = request.args.get('page', 1, type=int)

        start_date = None
        end_date = None

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid start date format. Use YYYY-MM-DD.', 'error')

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid end date format. Use YYYY-MM-DD.', 'error')

        pagination = AttendanceService.get_filtered_attendance(
            department=department if department else None,
            student_name=student_name if student_name else None,
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=20
        )

        departments = StudentService.get_departments()

        filters = {
            'start_date': start_date_str,
            'end_date': end_date_str,
            'department': department,
            'student_name': student_name
        }

        return render_template(
            'reports.html',
            records=pagination,
            departments=departments,
            filters=filters,
            page=page,
            total_pages=pagination.pages
        )
    except Exception as e:
        flash(f'Error loading reports: {str(e)}', 'error')
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
            'reports.html',
            records=EmptyPagination(),
            departments=[],
            filters={'start_date': '', 'end_date': '', 'department': '', 'student_name': ''},
            page=1,
            total_pages=1
        )


@reports_bp.route('/export')
@login_required
def export():
    """Export filtered report data as Excel or CSV.

    Query params:
        start_date: Start date (YYYY-MM-DD, required).
        end_date: End date (YYYY-MM-DD, required).
        department: Optional department filter.
        format: 'excel' or 'csv' (default: 'excel').
    """
    try:
        start_date_str = request.args.get('start_date', '').strip()
        end_date_str = request.args.get('end_date', '').strip()
        department = request.args.get('department', '').strip() or None
        export_format = request.args.get('format', 'excel')

        if not start_date_str or not end_date_str:
            flash('Start date and end date are required for export.', 'error')
            return redirect(url_for('reports.index'))

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD.', 'error')
            return redirect(url_for('reports.index'))

        if start_date > end_date:
            flash('Start date cannot be after end date.', 'error')
            return redirect(url_for('reports.index'))

        filename_suffix = (
            f'{start_date.strftime("%Y_%m_%d")}_to_'
            f'{end_date.strftime("%Y_%m_%d")}'
        )

        if export_format == 'csv':
            buffer = ExportService.export_csv(start_date, end_date, department)
            filename = f'report_{filename_suffix}.csv'
            mimetype = 'text/csv'
        else:
            buffer = ExportService.export_excel(
                start_date, end_date, department
            )
            filename = f'report_{filename_suffix}.xlsx'
            mimetype = (
                'application/vnd.openxmlformats-officedocument'
                '.spreadsheetml.sheet'
            )

        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )

    except Exception as e:
        flash(f'Error exporting report: {str(e)}', 'error')
        return redirect(url_for('reports.index'))
