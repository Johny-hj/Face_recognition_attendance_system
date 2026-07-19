"""
Attendance Service.

Provides attendance marking, querying, filtering, statistics,
and dashboard data aggregation.
"""

from datetime import date, time, datetime, timedelta
from sqlalchemy import func, and_
from models import db
from models.attendance import Attendance
from models.student import Student


class AttendanceService:
    """Service class for attendance operations."""

    @staticmethod
    def mark_attendance(student_id, confidence=None, status='Present'):
        """Mark attendance for a student. Enforces once-per-day rule.

        Args:
            student_id: Database ID of the student.
            confidence: Recognition confidence score (0.0 - 1.0).
            status: Attendance status ('Present', 'Late', etc.).

        Returns:
            Tuple of (Attendance instance, message string).
            Message is 'already_marked' if attendance exists for today,
            or 'marked' on success.
        """
        today = date.today()
        existing = Attendance.query.filter_by(
            student_id=student_id, date=today
        ).first()
        if existing:
            return existing, 'already_marked'

        attendance = Attendance(
            student_id=student_id,
            date=today,
            time=datetime.now().time(),
            status=status,
            confidence=confidence
        )
        db.session.add(attendance)
        db.session.commit()
        return attendance, 'marked'

    @staticmethod
    def get_today_attendance():
        """Get all attendance records for today, ordered by time descending."""
        today = date.today()
        return Attendance.query.filter_by(date=today)\
            .order_by(Attendance.time.desc()).all()

    @staticmethod
    def get_attendance_by_date(target_date):
        """Get all attendance records for a specific date."""
        return Attendance.query.filter_by(date=target_date)\
            .order_by(Attendance.time.desc()).all()

    @staticmethod
    def get_attendance_range(start_date, end_date):
        """Get attendance records within a date range (inclusive)."""
        return Attendance.query.filter(
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).order_by(Attendance.date.desc(), Attendance.time.desc()).all()

    @staticmethod
    def get_student_attendance(student_id, start_date=None, end_date=None):
        """Get attendance records for a specific student with optional date filters."""
        query = Attendance.query.filter_by(student_id=student_id)
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        return query.order_by(Attendance.date.desc()).all()

    @staticmethod
    def get_stats():
        """Get dashboard statistics including counts, weekly trend, and department data.

        Returns:
            Dict with keys: total_students, today_present, today_absent,
            today_late, recognition_rate, week_data, dept_data.
        """
        today = date.today()
        total_students = Student.query.count()
        today_present = Attendance.query.filter_by(
            date=today, status='Present'
        ).count()
        today_late = Attendance.query.filter_by(
            date=today, status='Late'
        ).count()
        today_total = today_present + today_late
        today_absent = total_students - today_total

        # Weekly attendance data for chart (last 7 days)
        week_data = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            count = Attendance.query.filter_by(date=d).count()
            week_data.append({
                'date': d.strftime('%a'),
                'count': count
            })

        # Department distribution
        dept_data = db.session.query(
            Student.department, func.count(Student.id)
        ).group_by(Student.department).all()

        # Average recognition confidence for today
        avg_confidence = db.session.query(
            func.avg(Attendance.confidence)
        ).filter_by(date=today).scalar()

        return {
            'total_students': total_students,
            'today_present': today_present,
            'today_absent': max(0, today_absent),
            'today_late': today_late,
            'recognition_rate': round((avg_confidence or 0) * 100, 1),
            'week_data': week_data,
            'dept_data': [
                {'department': d, 'count': c} for d, c in dept_data
            ],
        }

    @staticmethod
    def get_recent_attendance(limit=10):
        """Get the most recent attendance records."""
        return Attendance.query.order_by(
            Attendance.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def get_filtered_attendance(department=None, student_name=None,
                                 start_date=None, end_date=None,
                                 page=1, per_page=20):
        """Get paginated attendance records with optional filters.

        Args:
            department: Filter by student department.
            student_name: Filter by student name (partial match).
            start_date: Filter records on or after this date.
            end_date: Filter records on or before this date.
            page: Page number for pagination.
            per_page: Records per page.

        Returns:
            SQLAlchemy Pagination object.
        """
        query = Attendance.query.join(Student)
        if department:
            query = query.filter(Student.department == department)
        if student_name:
            query = query.filter(Student.name.ilike(f'%{student_name}%'))
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        query = query.order_by(Attendance.date.desc(), Attendance.time.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)
