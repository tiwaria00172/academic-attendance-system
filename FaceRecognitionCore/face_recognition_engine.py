"""
Face Recognition Core System - Face Recognition Engine
========================================================
Core face detection and 128D encoding extraction using dlib ResNet-34.
Deterministic: same image always produces the same encoding.
"""

import face_recognition
import numpy as np
import cv2
import time
from config import Config
from image_processor import ImageProcessor


class FaceRecognitionEngine:
    """
    Core face recognition engine.
    Detects faces and extracts 128-dimensional encodings.
    """

    def __init__(self):
        self.config = Config
        self.image_processor = ImageProcessor()

    # ─── Face Detection ──────────────────────────────────────────────────

    def detect_faces(self, image, upsample=None):
        """
        Detect face locations in an image using HOG or CNN model.
        Includes native adaptive multi-scale upsampling fallback for university classrooms.
        """
        try:
            if upsample is None:
                upsample = getattr(self.config, 'UPSAMPLE_CLASSROOM', 1)

            face_locations = face_recognition.face_locations(
                image,
                number_of_times_to_upsample=upsample,
                model=self.config.FACE_DETECTION_MODEL
            )

            # Adaptive fallback: if no faces found, progressively zoom up to UPSAMPLE_MAX
            max_zoom = getattr(self.config, 'UPSAMPLE_MAX', 3)
            while len(face_locations) == 0 and upsample < max_zoom:
                upsample += 1
                face_locations = face_recognition.face_locations(
                    image,
                    number_of_times_to_upsample=upsample,
                    model=self.config.FACE_DETECTION_MODEL
                )

            if len(face_locations) > self.config.MAX_FACES_PER_IMAGE:
                print(
                    f'Warning: {len(face_locations)} faces detected, '
                    f'exceeds limit of {self.config.MAX_FACES_PER_IMAGE}'
                )

            return face_locations

        except Exception as e:
            raise ValueError(f'Face detection failed: {str(e)}')

    # ─── Face Encoding ───────────────────────────────────────────────────

    def extract_face_encoding(self, image, face_location):
        """
        Extract 128D face encoding from a single detected face.

        Args:
            image: np.ndarray in RGB format
            face_location: (top, right, bottom, left) bounding box

        Returns:
            np.ndarray: 128-dimensional encoding vector (float64)

        Raises:
            ValueError: If encoding extraction fails
        """
        try:
            encodings = face_recognition.face_encodings(
                image,
                [face_location],
                num_jitters=self.config.NUM_JITTERS
            )

            if not encodings:
                raise ValueError('No encoding could be extracted for this face')

            # Ensure correct dtype for deterministic precision
            encoding = np.array(encodings[0], dtype=self.config.ENCODING_PRECISION)

            return encoding

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f'Face encoding extraction failed: {str(e)}')

    # ─── Complete Pipeline ───────────────────────────────────────────────

    def extract_all_face_encodings(self, image_path, upsample=None):
        """
        Complete pipeline: preprocess → detect → encode all faces.

        Args:
            image_path: Path to image file
            upsample: Optional zoom scale for detection

        Returns:
            dict:
                - success (bool)
                - encodings (list of 128D numpy arrays)
                - face_locations (list of bounding boxes)
                - quality_info (quality assessment dict)
                - face_count (int)
                - processing_time_ms (float)
                - error (str, only if success=False)
        """
        start_time = time.time()

        try:
            # Step 1: Preprocess image (quality check + enhancement)
            image_bgr, quality_info = self.image_processor.preprocess_image(
                image_path
            )

            # Convert BGR → RGB for face_recognition library
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

            # Step 2: Detect faces with native multi-scale fallback
            face_locations = self.detect_faces(image_rgb, upsample=upsample)

            if not face_locations:
                raise ValueError('No faces detected in image')

            # Step 3: Extract encodings for each detected face
            encodings = []
            for face_location in face_locations:
                encoding = self.extract_face_encoding(image_rgb, face_location)
                encodings.append(encoding)

            processing_time_ms = (time.time() - start_time) * 1000

            return {
                'success': True,
                'encodings': encodings,
                'face_locations': face_locations,
                'quality_info': quality_info,
                'face_count': len(encodings),
                'processing_time_ms': processing_time_ms
            }

        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000

            return {
                'success': False,
                'error': str(e),
                'encodings': [],
                'face_locations': [],
                'face_count': 0,
                'processing_time_ms': processing_time_ms
            }

    # ─── Student Encoding (Single Face) ──────────────────────────────────

    def extract_student_encoding(self, student_photo_path):
        """
        Extract face encoding from a student reference photo.
        The photo must contain exactly one clear face.

        Args:
            student_photo_path: Path to student's reference photo

        Returns:
            np.ndarray: 128D encoding vector, or None if extraction failed
        """
        result = self.extract_all_face_encodings(
            student_photo_path,
            upsample=getattr(self.config, 'UPSAMPLE_TRAINING', 2)
        )

        if not result['success']:
            print(f'  Failed to extract encoding: {result["error"]}')
            return None

        if result['face_count'] != 1:
            print(
                f'  Expected 1 face in student photo, '
                f'found {result["face_count"]}'
            )
            # If multiple faces found, use the largest face (most prominent)
            if result['face_count'] > 1:
                face_locations = result['face_locations']
                areas = [
                    (bottom - top) * (right - left)
                    for (top, right, bottom, left) in face_locations
                ]
                largest_idx = int(np.argmax(areas))
                print(f'  Using largest face (index {largest_idx})')
                return result['encodings'][largest_idx]
            return None

        return result['encodings'][0]
