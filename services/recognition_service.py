"""
Face Recognition Service.

Provides face encoding, recognition, and duplicate detection
using the face_recognition library and numpy.
"""

import face_recognition
import numpy as np
import pickle
from models import db
from models.student import Student


class RecognitionService:
    """Service class for face recognition operations."""

    @staticmethod
    def encode_face(image_path):
        """Generate face encoding from an image file.

        Args:
            image_path: Path to the image file.

        Returns:
            numpy array of the face encoding, or None if no face detected.
        """
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            return encodings[0]
        return None

    @staticmethod
    def encode_face_from_array(image_array):
        """Generate face encoding from a numpy array (e.g., from OpenCV frame).

        Args:
            image_array: BGR numpy array from OpenCV.

        Returns:
            List of (encoding, location) tuples for each detected face.
        """
        rgb_image = np.ascontiguousarray(image_array[:, :, ::-1])  # BGR to RGB (must be contiguous for dlib)
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        return list(zip(face_encodings, face_locations))

    @staticmethod
    def save_encoding(student, encoding):
        """Save face encoding to student record as pickled numpy array.

        Args:
            student: Student model instance.
            encoding: numpy array face encoding.
        """
        student.face_encoding = pickle.dumps(encoding)
        db.session.commit()

    @staticmethod
    def load_all_encodings():
        """Load all known face encodings from the database.

        Returns:
            Dict mapping student.id -> (encoding, student) tuples.
        """
        students = Student.query.filter(Student.face_encoding.isnot(None)).all()
        known = {}
        for s in students:
            try:
                encoding = pickle.loads(s.face_encoding)
                known[s.id] = (encoding, s)
            except Exception:
                continue
        return known

    @staticmethod
    def recognize_faces(frame, tolerance=0.6):
        """Recognize faces in a video frame.

        Args:
            frame: BGR numpy array from OpenCV.
            tolerance: Maximum face distance to consider a match (lower = stricter).

        Returns:
            List of dicts with keys: student, confidence, location, known.
        """
        known = RecognitionService.load_all_encodings()
        if not known:
            return []

        known_ids = list(known.keys())
        known_encodings = [known[sid][0] for sid in known_ids]

        results = RecognitionService.encode_face_from_array(frame)
        recognized = []

        for encoding, location in results:
            distances = face_recognition.face_distance(known_encodings, encoding)
            if len(distances) > 0:
                best_idx = np.argmin(distances)
                best_distance = distances[best_idx]
                confidence = 1.0 - best_distance

                if best_distance <= tolerance:
                    student = known[known_ids[best_idx]][1]
                    recognized.append({
                        'student': student,
                        'confidence': float(confidence),
                        'location': location,
                        'known': True
                    })
                else:
                    recognized.append({
                        'student': None,
                        'confidence': float(confidence),
                        'location': location,
                        'known': False
                    })
            else:
                recognized.append({
                    'student': None,
                    'confidence': 0.0,
                    'location': location,
                    'known': False
                })

        return recognized

    @staticmethod
    def check_duplicate(encoding, tolerance=0.5):
        """Check if a face encoding already exists in the database.

        Args:
            encoding: numpy array face encoding to check.
            tolerance: Maximum face distance to consider a duplicate.

        Returns:
            Student instance if duplicate found, None otherwise.
        """
        known = RecognitionService.load_all_encodings()
        for sid, (known_enc, student) in known.items():
            distance = face_recognition.face_distance([known_enc], encoding)[0]
            if distance <= tolerance:
                return student
        return None
