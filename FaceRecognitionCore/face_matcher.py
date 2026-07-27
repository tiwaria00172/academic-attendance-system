"""
Face Recognition Core System - Face Matcher
=============================================
Vectorized face matching using L2 Euclidean distance.
"""

import numpy as np
from config import Config
import time


class FaceMatcher:
    """Match detected faces against a student encoding database."""

    def __init__(self):
        self.config = Config

    def calculate_distance(self, encoding1, encoding2):
        """L2 Euclidean distance between two 128D encodings."""
        return float(np.linalg.norm(encoding1 - encoding2))

    def calculate_similarity(self, distance):
        """Convert L2 distance to similarity score [0,1]."""
        return float(max(0.0, min(1.0, 1.0 - distance)))

    def match_face_to_database(self, detected_encoding, student_database):
        """
        Match one detected face to all students (vectorized).

        Returns dict with best_match, alternatives, is_ambiguous, match_type.
        """
        if not student_database:
            return {
                'best_match': None, 'alternatives': [],
                'is_ambiguous': False, 'match_type': 'not_found'
            }

        student_ids = sorted(student_database.keys())
        encodings_matrix = np.array([
            student_database[sid]['encoding'] for sid in student_ids
        ], dtype=self.config.ENCODING_PRECISION)

        distances = np.linalg.norm(encodings_matrix - detected_encoding, axis=1)
        similarities = np.clip(1.0 - distances, 0.0, 1.0)
        sorted_indices = np.argsort(similarities)[::-1]

        best_idx = sorted_indices[0]
        best_sid = student_ids[best_idx]
        best_sim = float(similarities[best_idx])

        best_match = {
            'student_id': best_sid,
            'name': student_database[best_sid]['name'],
            'roll_number': student_database[best_sid].get('roll_number', 'N/A'),
            'similarity': best_sim
        }

        alternatives = []
        for i in range(1, min(4, len(sorted_indices))):
            idx = sorted_indices[i]
            sid = student_ids[idx]
            alternatives.append({
                'student_id': sid,
                'name': student_database[sid]['name'],
                'roll_number': student_database[sid].get('roll_number', 'N/A'),
                'similarity': float(similarities[idx])
            })

        is_ambiguous = False
        if len(sorted_indices) > 1 and best_sim < self.config.FACE_CONFIDENCE_AUTO:
            runner_up = float(similarities[sorted_indices[1]])
            if (best_sim - runner_up) < self.config.FACE_AMBIGUITY_THRESHOLD:
                is_ambiguous = True

        if best_sim >= self.config.FACE_CONFIDENCE_AUTO:
            match_type = 'auto_marked'
        elif best_sim >= self.config.FACE_CONFIDENCE_MANUAL:
            match_type = 'needs_confirmation'
        else:
            match_type = 'not_found'

        return {
            'best_match': best_match, 'alternatives': alternatives,
            'is_ambiguous': is_ambiguous, 'match_type': match_type
        }

    def match_all_faces(self, detected_encodings, student_database):
        """Match multiple detected faces against the student database."""
        start_time = time.time()
        results = {
            'auto_marked': [], 'needs_confirmation': [], 'not_found': [],
            'total_detected': len(detected_encodings), 'processing_time_ms': 0
        }

        for face_idx, encoding in enumerate(detected_encodings):
            match_result = self.match_face_to_database(encoding, student_database)
            match_type = match_result['match_type']

            if match_type == 'auto_marked':
                results['auto_marked'].append({
                    'face_index': face_idx, **match_result['best_match']
                })
            elif match_type == 'needs_confirmation':
                results['needs_confirmation'].append({
                    'face_index': face_idx,
                    'best_match': match_result['best_match'],
                    'alternatives': match_result['alternatives'],
                    'is_ambiguous': match_result['is_ambiguous']
                })
            else:
                results['not_found'].append({
                    'face_index': face_idx,
                    'best_match': match_result['best_match']
                    if match_result['best_match'] and match_result['best_match']['similarity'] > 0.3
                    else None
                })

        results['processing_time_ms'] = (time.time() - start_time) * 1000
        return results
