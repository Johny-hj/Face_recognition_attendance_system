"""
Student Service.

Provides CRUD operations, search, face registration,
and department listing for student management.
"""

import os
import pickle
from models import db
from models.student import Student
from services.recognition_service import RecognitionService
from utils.helpers import save_uploaded_file, generate_student_id


class StudentService:
    """Service class for student CRUD and face registration operations."""

    @staticmethod
    def create_student(data, photo_file=None, upload_folder=None):
        """Create a new student record with optional photo and face encoding.

        Args:
            data: Dict with keys: name, roll_number, department,
                  and optional: year, section, email, phone.
            photo_file: Uploaded photo file object (werkzeug FileStorage).
            upload_folder: Absolute path to the upload directory.

        Returns:
            The newly created Student instance.
        """
        student = Student(
            student_id=generate_student_id(),
            name=data['name'],
            roll_number=data['roll_number'],
            department=data['department'],
            year=data.get('year', ''),
            section=data.get('section', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            photo=data.get('photo', '')
        )

        if photo_file and upload_folder:
            filename = save_uploaded_file(
                photo_file, upload_folder, prefix=student.student_id
            )
            if filename:
                student.photo = filename
                # Attempt to generate face encoding from the uploaded photo
                photo_path = os.path.join(upload_folder, filename)
                encoding = RecognitionService.encode_face(photo_path)
                if encoding is not None:
                    student.face_encoding = pickle.dumps(encoding)

        db.session.add(student)
        db.session.commit()
        return student

    @staticmethod
    def update_student(student_id, data, photo_file=None, upload_folder=None):
        """Update an existing student record.

        Args:
            student_id: Database ID of the student to update.
            data: Dict with updated field values.
            photo_file: Optional new photo file.
            upload_folder: Absolute path to the upload directory.

        Returns:
            The updated Student instance.
        """
        student = Student.query.get_or_404(student_id)
        student.name = data.get('name', student.name)
        student.roll_number = data.get('roll_number', student.roll_number)
        student.department = data.get('department', student.department)
        student.year = data.get('year', student.year)
        student.section = data.get('section', student.section)
        student.email = data.get('email', student.email)
        student.phone = data.get('phone', student.phone)
        if data.get('photo'):
            student.photo = data['photo']

        if photo_file and upload_folder:
            # Delete old photo file if it exists
            if student.photo:
                old_path = os.path.join(upload_folder, student.photo)
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename = save_uploaded_file(
                photo_file, upload_folder, prefix=student.student_id
            )
            if filename:
                student.photo = filename
                photo_path = os.path.join(upload_folder, filename)
                encoding = RecognitionService.encode_face(photo_path)
                if encoding is not None:
                    student.face_encoding = pickle.dumps(encoding)

        db.session.commit()
        return student

    @staticmethod
    def delete_student(student_id, upload_folder=None):
        """Delete a student and their associated photo file.

        Args:
            student_id: Database ID of the student to delete.
            upload_folder: Absolute path to the upload directory.
        """
        student = Student.query.get_or_404(student_id)
        if student.photo and upload_folder:
            photo_path = os.path.join(upload_folder, student.photo)
            if os.path.exists(photo_path):
                os.remove(photo_path)
        db.session.delete(student)
        db.session.commit()

    @staticmethod
    def get_all_students():
        """Get all students ordered by most recently created."""
        return Student.query.order_by(Student.created_at.desc()).all()

    @staticmethod
    def search_students(query):
        """Search students by name, roll number, student ID, or department.

        Args:
            query: Search string for partial matching.

        Returns:
            List of matching Student instances.
        """
        return Student.query.filter(
            db.or_(
                Student.name.ilike(f'%{query}%'),
                Student.roll_number.ilike(f'%{query}%'),
                Student.student_id.ilike(f'%{query}%'),
                Student.department.ilike(f'%{query}%')
            )
        ).all()

    @staticmethod
    def get_departments():
        """Get list of all distinct department names.

        Returns:
            List of department name strings.
        """
        departments = db.session.query(Student.department).distinct().all()
        return [d[0] for d in departments if d[0]]

    @staticmethod
    def register_face(student_id, image_path):
        """Register a face encoding for a student from an image file.

        Args:
            student_id: Database ID of the student.
            image_path: Path to the image file containing the student's face.

        Returns:
            Tuple of (Student or None, message string).
        """
        student = Student.query.get_or_404(student_id)
        encoding = RecognitionService.encode_face(image_path)
        if encoding is not None:
            # Check for duplicate face registrations
            duplicate = RecognitionService.check_duplicate(encoding)
            if duplicate and duplicate.id != student.id:
                return None, f'Face already registered for {duplicate.name}'
            RecognitionService.save_encoding(student, encoding)
            return student, 'Face registered successfully'
        return None, 'No face detected in the image'
