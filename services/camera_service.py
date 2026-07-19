"""
Camera Service.

Provides video capture, frame encoding/decoding, and MJPEG streaming
using OpenCV for both server-side and client-side camera workflows.
"""

import cv2
import numpy as np
import base64
from services.recognition_service import RecognitionService


class CameraService:
    """Service class for camera and video frame operations."""

    _camera = None

    @classmethod
    def get_camera(cls):
        """Get or initialize the camera instance.

        Returns:
            OpenCV VideoCapture object.
        """
        if cls._camera is None or not cls._camera.isOpened():
            cls._camera = cv2.VideoCapture(0)
            cls._camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cls._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return cls._camera

    @classmethod
    def release_camera(cls):
        """Release the camera resource."""
        if cls._camera is not None:
            cls._camera.release()
            cls._camera = None

    @classmethod
    def get_frame(cls):
        """Capture a single frame from the camera.

        Returns:
            BGR numpy array of the frame, or None on failure.
        """
        camera = cls.get_camera()
        success, frame = camera.read()
        if success:
            return frame
        return None

    @staticmethod
    def frame_to_base64(frame):
        """Encode a BGR frame as a base64 JPEG string.

        Args:
            frame: BGR numpy array.

        Returns:
            Base64-encoded string of the JPEG image.
        """
        _, buffer = cv2.imencode('.jpg', frame)
        return base64.b64encode(buffer).decode('utf-8')

    @staticmethod
    def base64_to_frame(b64_string):
        """Decode a base64 string back to a BGR numpy array.

        Args:
            b64_string: Base64-encoded JPEG string.

        Returns:
            BGR numpy array of the decoded image.
        """
        img_data = base64.b64decode(b64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    @classmethod
    def generate_frames(cls):
        """Generator for streaming MJPEG video frames.

        Yields:
            Bytes for each MJPEG frame boundary and JPEG data.
        """
        while True:
            frame = cls.get_frame()
            if frame is None:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
