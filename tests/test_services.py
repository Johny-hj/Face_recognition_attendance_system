from services.attendance_service import AttendanceService
from services.student_service import StudentService
from services.export_service import ExportService
from models.student import Student
from datetime import date

def test_student_service_create(app, db):
    with app.app_context():
        data = {
            'name': 'Service Test',
            'roll_number': 'SRV001',
            'department': 'Testing',
            'year': '1st',
            'section': 'A',
            'email': 'srv@test.com',
            'phone': '1234567890'
        }
        student = StudentService.create_student(data)
        assert student.name == 'Service Test'
        assert student.roll_number == 'SRV001'
        assert student.student_id is not None

def test_student_service_search(app, db):
    with app.app_context():
        data = {'name': 'Search Me', 'roll_number': 'FIND001', 'department': 'Finding'}
        StudentService.create_student(data)
        results = StudentService.search_students('Search')
        assert len(results) > 0
        assert results[0].name == 'Search Me'

def test_attendance_service_mark(app, db):
    with app.app_context():
        # Create a student first
        student = StudentService.create_student({'name': 'Att Test', 'roll_number': 'ATT001', 'department': 'CS'})
        
        # Mark attendance
        att, msg = AttendanceService.mark_attendance(student.id, confidence=0.99, status='Present')
        assert att is not None
        assert msg == 'marked'
        assert att.student_id == student.id
        assert att.status == 'Present'

def test_attendance_service_prevent_duplicate(app, db):
    with app.app_context():
        student = StudentService.create_student({'name': 'Dup Test', 'roll_number': 'DUP001', 'department': 'CS'})
        
        # Mark once
        att1, msg1 = AttendanceService.mark_attendance(student.id, confidence=0.99)
        assert msg1 == 'marked'
        
        # Try to mark again on the same day
        att2, msg2 = AttendanceService.mark_attendance(student.id, confidence=0.88)
        assert msg2 == 'already_marked'
        assert att2.id == att1.id

def test_attendance_service_stats(app, db):
    with app.app_context():
        student = StudentService.create_student({'name': 'Stat Test', 'roll_number': 'STAT001', 'department': 'CS'})
        AttendanceService.mark_attendance(student.id, confidence=0.95)
        
        stats = AttendanceService.get_stats()
        assert stats['total_students'] >= 1
        assert stats['today_present'] >= 1
        assert stats['recognition_rate'] == 95.0
        assert len(stats['week_data']) == 7

def test_export_service(app, db):
    with app.app_context():
        student = StudentService.create_student({'name': 'Exp Test', 'roll_number': 'EXP001', 'department': 'IT'})
        AttendanceService.mark_attendance(student.id, confidence=0.9)
        
        # Test Excel export
        excel_buffer = ExportService.export_excel(date.today(), date.today())
        assert excel_buffer is not None
        assert excel_buffer.getbuffer().nbytes > 0
