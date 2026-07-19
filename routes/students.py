"""
Student Management Routes.

Provides CRUD operations, search API, and face registration
endpoints for managing students.
"""

import os
import uuid
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, jsonify, current_app
)
from flask_login import login_required
from services.student_service import StudentService
from services.camera_service import CameraService
from utils.helpers import allowed_file, validate_email, validate_phone

students_bp = Blueprint('students', __name__, url_prefix='/students')


@students_bp.route('/')
@login_required
def list_students():
    """List all students with search, department filter, and pagination."""
    try:
        search = request.args.get('search', '').strip()
        department = request.args.get('department', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = 20

        if search:
            students = StudentService.search_students(search)
        else:
            students = StudentService.get_all_students()

        # Apply department filter
        if department:
            students = [s for s in students if s.department == department]

        # Manual pagination
        total = len(students)
        total_pages = max(1, (total + per_page - 1) // per_page)
        page = max(1, min(page, total_pages))
        start = (page - 1) * per_page
        end = start + per_page
        paginated_students = students[start:end]

        departments = StudentService.get_departments()

        return render_template(
            'students/list.html',
            students=paginated_students,
            departments=departments,
            search=search,
            selected_dept=department,
            page=page,
            total_pages=total_pages,
            total=total
        )
    except Exception as e:
        flash(f'Error loading students: {str(e)}', 'error')
        return render_template(
            'students/list.html',
            students=[],
            departments=[],
            search='',
            selected_dept='',
            page=1,
            total_pages=1,
            total=0
        )


@students_bp.route('/add', methods=['POST'])
@login_required
def add_student():
    """Create a new student from form data with optional photo upload."""
    try:
        name = request.form.get('name', '').strip()
        roll_number = request.form.get('roll_number', '').strip()
        department = request.form.get('department', '').strip()

        # Validate required fields
        if not name or not roll_number or not department:
            flash('Name, Roll Number, and Department are required.', 'error')
            return redirect(url_for('students.list_students'))

        # Validate optional fields
        email = request.form.get('email', '').strip()
        if email and not validate_email(email):
            flash('Invalid email address.', 'error')
            return redirect(url_for('students.list_students'))

        phone = request.form.get('phone', '').strip()
        if phone and not validate_phone(phone):
            flash('Invalid phone number.', 'error')
            return redirect(url_for('students.list_students'))

        data = {
            'name': name,
            'roll_number': roll_number,
            'department': department,
            'year': request.form.get('year', '').strip(),
            'section': request.form.get('section', '').strip(),
            'email': email,
            'phone': phone
        }

        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        os.makedirs(upload_folder, exist_ok=True)
        photo_file = None

        # Handle base64 selfie from webcam
        photo_data = request.form.get('photo_data', '').strip()
        if photo_data and photo_data.startswith('data:image'):
            import base64
            header, encoded = photo_data.split(',', 1)
            img_bytes = base64.b64decode(encoded)
            filename = f"selfie_{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(upload_folder, filename)
            with open(filepath, 'wb') as f:
                f.write(img_bytes)
            data['photo'] = filename
        else:
            # Fallback: file upload
            photo_file = request.files.get('photo')
            if photo_file and photo_file.filename:
                if not allowed_file(photo_file.filename):
                    flash('Invalid file type. Please upload an image file.', 'error')
                    return redirect(url_for('students.list_students'))

        student = StudentService.create_student(
            data,
            photo_file=photo_file,
            upload_folder=upload_folder
        )

        # If selfie was used, also generate face encoding from the saved photo
        if data.get('photo') and not photo_file:
            import pickle
            from services.recognition_service import RecognitionService
            photo_path = os.path.join(upload_folder, data['photo'])
            encoding = RecognitionService.encode_face(photo_path)
            if encoding is not None:
                from models import db
                student.face_encoding = pickle.dumps(encoding)
                db.session.commit()

        flash(f'Student {student.name} added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding student: {str(e)}', 'error')

    return redirect(url_for('students.list_students'))


@students_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit_student(id):
    """Update an existing student's information."""
    try:
        email = request.form.get('email', '').strip()
        if email and not validate_email(email):
            flash('Invalid email address.', 'error')
            return redirect(url_for('students.list_students'))

        phone = request.form.get('phone', '').strip()
        if phone and not validate_phone(phone):
            flash('Invalid phone number.', 'error')
            return redirect(url_for('students.list_students'))

        data = {
            'name': request.form.get('name', '').strip(),
            'roll_number': request.form.get('roll_number', '').strip(),
            'department': request.form.get('department', '').strip(),
            'year': request.form.get('year', '').strip(),
            'section': request.form.get('section', '').strip(),
            'email': email,
            'phone': phone
        }

        # Validate required fields
        if not data['name'] or not data['roll_number'] or not data['department']:
            flash('Name, Roll Number, and Department are required.', 'error')
            return redirect(url_for('students.list_students'))

        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        os.makedirs(upload_folder, exist_ok=True)
        photo_file = None

        # Handle base64 selfie from webcam
        photo_data = request.form.get('photo_data', '').strip()
        if photo_data and photo_data.startswith('data:image'):
            import base64
            header, encoded = photo_data.split(',', 1)
            img_bytes = base64.b64decode(encoded)
            filename = f"selfie_{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(upload_folder, filename)
            with open(filepath, 'wb') as f:
                f.write(img_bytes)
            data['photo'] = filename
        else:
            photo_file = request.files.get('photo')
            if photo_file and photo_file.filename:
                if not allowed_file(photo_file.filename):
                    flash('Invalid file type.', 'error')
                    return redirect(url_for('students.list_students'))

        student = StudentService.update_student(
            id,
            data,
            photo_file=photo_file if photo_file and photo_file.filename else None,
            upload_folder=upload_folder
        )

        # If selfie was used, also generate face encoding from the saved photo
        if data.get('photo') and not (photo_file and photo_file.filename):
            import pickle
            from services.recognition_service import RecognitionService
            photo_path = os.path.join(upload_folder, data['photo'])
            encoding = RecognitionService.encode_face(photo_path)
            if encoding is not None:
                from models import db
                student.face_encoding = pickle.dumps(encoding)
                db.session.commit()

        flash(f'Student {student.name} updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating student: {str(e)}', 'error')

    return redirect(url_for('students.list_students'))


@students_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_student(id):
    """Delete a student and their associated files."""
    try:
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        StudentService.delete_student(id, upload_folder=upload_folder)
        flash('Student deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting student: {str(e)}', 'error')

    return redirect(url_for('students.list_students'))


@students_bp.route('/search')
@login_required
def search_students():
    """JSON API for AJAX student search."""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': True, 'students': []})

        students = StudentService.search_students(query)
        students_data = [s.to_dict() for s in students]
        return jsonify({
            'success': True,
            'students': students_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@students_bp.route('/register-face/<int:id>', methods=['GET'])
@login_required
def register_face_page(id):
    """Render the face registration page for a student."""
    try:
        from models.student import Student
        student = Student.query.get_or_404(id)
        return render_template('students/register_face.html', student=student)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('students.list_students'))


@students_bp.route('/register-face/<int:id>', methods=['POST'])
@login_required
def register_face(id):
    """Handle face registration from image upload or webcam capture.

    Accepts either:
    - A file upload via 'photo' field
    - A base64-encoded webcam capture via 'image_data' JSON field

    Returns JSON response with registration result.
    """
    try:
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        image_path = None

        # Check for file upload
        photo_file = request.files.get('photo')
        if photo_file and photo_file.filename:
            if not allowed_file(photo_file.filename):
                return jsonify({
                    'success': False,
                    'message': 'Invalid file type.'
                }), 400

            from utils.helpers import save_uploaded_file
            filename = save_uploaded_file(
                photo_file, upload_folder, prefix=f'face_reg_{id}'
            )
            if filename:
                image_path = os.path.join(upload_folder, filename)

        # Check for base64 webcam capture
        if not image_path:
            image_data = None
            if request.is_json:
                image_data = request.json.get('image_data', '')
            else:
                image_data = request.form.get('image_data', '')

            if image_data:
                # Strip data URL prefix if present
                if ',' in image_data:
                    image_data = image_data.split(',', 1)[1]

                frame = CameraService.base64_to_frame(image_data)
                if frame is not None:
                    import cv2
                    filename = f'face_reg_{id}_{uuid.uuid4().hex[:8]}.jpg'
                    image_path = os.path.join(upload_folder, filename)
                    cv2.imwrite(image_path, frame)

        if not image_path:
            return jsonify({
                'success': False,
                'message': 'No image provided.'
            }), 400

        student, message = StudentService.register_face(id, image_path)

        # Clean up temporary registration image
        if image_path and os.path.exists(image_path):
            if 'face_reg_' in os.path.basename(image_path):
                os.remove(image_path)

        if student:
            return jsonify({
                'success': True,
                'message': message,
                'student': student.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error during face registration: {str(e)}'
        }), 500
