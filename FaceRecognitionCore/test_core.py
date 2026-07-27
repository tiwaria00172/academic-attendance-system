"""
Face Recognition Core System - Test Suite
===========================================
End-to-end tests: determinism, encoding consistency, detection, matching.
"""

import os
import sys
import time
import numpy as np

# Add parent dir to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from image_processor import ImageProcessor
from face_recognition_engine import FaceRecognitionEngine
from face_matcher import FaceMatcher
from data_loader import StudentDatabase


class CoreSystemTest:
    """Test face recognition core system end-to-end."""

    def __init__(self):
        self.config = Config
        self.image_processor = ImageProcessor()
        self.engine = FaceRecognitionEngine()
        self.matcher = FaceMatcher()
        self.db_loader = StudentDatabase()
        self.results = {}

    def _get_first_training_image(self):
        """Get path to first training image."""
        files = sorted([
            f for f in os.listdir(self.config.TRAINING_DATA_DIR)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ])
        if not files:
            return None
        return os.path.join(self.config.TRAINING_DATA_DIR, files[0])

    def test_determinism(self):
        """Test that same image gives identical results every time."""
        print('\n' + '=' * 60)
        print('TEST 1: DETERMINISM')
        print('=' * 60)

        test_image = self._get_first_training_image()
        if not test_image:
            print('SKIP: No training images found')
            self.results['determinism'] = 'SKIP'
            return

        print(f'Image: {os.path.basename(test_image)}')
        encodings_list = []

        for run in range(5):
            result = self.engine.extract_all_face_encodings(test_image)
            if result['success']:
                encodings_list.append(result['encodings'][0])
                print(f'  Run {run+1}: {result["face_count"]} face(s), '
                      f'{result["processing_time_ms"]:.1f}ms')
            else:
                print(f'  Run {run+1}: FAILED - {result["error"]}')

        if len(encodings_list) < 2:
            print('FAIL: Could not extract enough encodings')
            self.results['determinism'] = 'FAIL'
            return

        all_identical = True
        for i in range(1, len(encodings_list)):
            diff = float(np.abs(encodings_list[i] - encodings_list[0]).max())
            if diff > 1e-6:
                all_identical = False
                print(f'  Run {i+1} differs (max diff: {diff})')

        if all_identical:
            print('PASS: All runs gave identical results')
            self.results['determinism'] = 'PASS'
        else:
            print('FAIL: Results differ between runs')
            self.results['determinism'] = 'FAIL'

    def test_encoding_consistency(self):
        """Test encoding reproducibility across separate extractions."""
        print('\n' + '=' * 60)
        print('TEST 2: ENCODING CONSISTENCY')
        print('=' * 60)

        test_image = self._get_first_training_image()
        if not test_image:
            print('SKIP: No training images')
            self.results['encoding_consistency'] = 'SKIP'
            return

        enc1 = self.engine.extract_student_encoding(test_image)
        enc2 = self.engine.extract_student_encoding(test_image)

        if enc1 is None or enc2 is None:
            print('FAIL: Could not extract encoding')
            self.results['encoding_consistency'] = 'FAIL'
            return

        max_diff = float(np.abs(enc1 - enc2).max())
        print(f'Max difference: {max_diff}')

        if max_diff < 1e-6:
            print('PASS: Encodings are identical')
            self.results['encoding_consistency'] = 'PASS'
        else:
            print(f'FAIL: Encodings differ (max diff: {max_diff})')
            self.results['encoding_consistency'] = 'FAIL'

    def test_face_detection(self):
        """Test face detection on test images."""
        print('\n' + '=' * 60)
        print('TEST 3: FACE DETECTION')
        print('=' * 60)

        # Try testing dir first, fall back to training dir
        test_dir = self.config.TESTING_DATA_DIR
        if not os.path.exists(test_dir) or not os.listdir(test_dir):
            test_dir = self.config.TRAINING_DATA_DIR
            print(f'No test images found, using training images instead')

        test_files = sorted([
            f for f in os.listdir(test_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ])[:5]

        if not test_files:
            print('SKIP: No images found')
            self.results['face_detection'] = 'SKIP'
            return

        print(f'Testing {len(test_files)} images...')
        total_faces = 0

        for img_file in test_files:
            img_path = os.path.join(test_dir, img_file)
            result = self.engine.extract_all_face_encodings(img_path)

            if result['success']:
                total_faces += result['face_count']
                print(f'  {img_file}: {result["face_count"]} face(s) '
                      f'({result["processing_time_ms"]:.0f}ms)')
            else:
                print(f'  {img_file}: FAILED - {result["error"]}')

        print(f'\nTotal faces detected: {total_faces}')

        if total_faces > 0:
            print('PASS: Face detection working')
            self.results['face_detection'] = 'PASS'
        else:
            print('FAIL: No faces detected')
            self.results['face_detection'] = 'FAIL'

    def test_matching_accuracy(self):
        """Test the complete matching pipeline."""
        print('\n' + '=' * 60)
        print('TEST 4: MATCHING ACCURACY')
        print('=' * 60)

        # Load student database
        print('Loading student database...')
        load_result = self.db_loader.load_students_from_folder(
            self.config.TRAINING_DATA_DIR
        )

        student_db = self.db_loader.get_database()
        print(f'\nLoaded {len(student_db)} students into database')

        if len(student_db) == 0:
            print('FAIL: No students loaded')
            self.results['matching_accuracy'] = 'FAIL'
            return

        self.db_loader.print_database_info()

        # Self-match test: each student should match themselves
        print('\n--- Self-Match Test ---')
        correct = 0
        total = 0

        for sid, info in sorted(student_db.items()):
            encoding = info['encoding']
            match = self.matcher.match_face_to_database(encoding, student_db)

            if match['best_match'] and match['best_match']['student_id'] == sid:
                correct += 1
                sim = match['best_match']['similarity']
                print(f'  {sid} ({info["name"]}): '
                      f'CORRECT match, similarity={sim:.2%}')
            else:
                matched_id = match['best_match']['student_id'] if match['best_match'] else 'None'
                print(f'  {sid}: WRONG match -> {matched_id}')
            total += 1

        accuracy = (correct / total * 100) if total > 0 else 0
        print(f'\nSelf-match accuracy: {correct}/{total} ({accuracy:.1f}%)')

        # Test on testing images if available
        test_dir = self.config.TESTING_DATA_DIR
        if os.path.exists(test_dir):
            test_files = sorted([
                f for f in os.listdir(test_dir)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ])[:3]

            if test_files:
                print('\n--- Class Photo Matching ---')
                for img_file in test_files:
                    img_path = os.path.join(test_dir, img_file)
                    result = self.engine.extract_all_face_encodings(img_path)

                    if not result['success']:
                        print(f'  {img_file}: Detection failed - {result["error"]}')
                        continue

                    match_result = self.matcher.match_all_faces(
                        result['encodings'], student_db
                    )

                    print(f'  {img_file}: {result["face_count"]} faces')
                    print(f'    Auto-marked: {len(match_result["auto_marked"])}')
                    print(f'    Needs confirmation: '
                          f'{len(match_result["needs_confirmation"])}')
                    print(f'    Not found: {len(match_result["not_found"])}')

                    for m in match_result['auto_marked'][:3]:
                        print(f'      -> {m["name"]}: {m["similarity"]:.2%}')

        if accuracy == 100:
            print('\nPASS: Matching pipeline working perfectly')
            self.results['matching_accuracy'] = 'PASS'
        elif accuracy >= 80:
            print('\nPASS: Matching pipeline working (acceptable accuracy)')
            self.results['matching_accuracy'] = 'PASS'
        else:
            print('\nFAIL: Low matching accuracy')
            self.results['matching_accuracy'] = 'FAIL'

    def run_all_tests(self):
        """Run all tests and print final report."""
        print('\n' + '#' * 60)
        print('  FACE RECOGNITION CORE SYSTEM - TEST SUITE')
        print('#' * 60)

        start = time.time()

        self.test_determinism()
        self.test_encoding_consistency()
        self.test_face_detection()
        self.test_matching_accuracy()

        elapsed = time.time() - start

        # Summary
        print('\n' + '=' * 60)
        print('TEST SUMMARY')
        print('=' * 60)

        for name, result in self.results.items():
            icon = {'PASS': 'PASS', 'FAIL': 'FAIL', 'SKIP': 'SKIP'}[result]
            print(f'  {name}: {icon}')

        passed = sum(1 for v in self.results.values() if v == 'PASS')
        total = len(self.results)

        print(f'\nTotal: {passed}/{total} passed in {elapsed:.1f}s')
        print('=' * 60)

        if all(v in ('PASS', 'SKIP') for v in self.results.values()):
            print('ALL TESTS PASSED - CORE SYSTEM READY')
        else:
            print('SOME TESTS FAILED - DEBUG REQUIRED')

        print('=' * 60)


if __name__ == '__main__':
    # Create directories
    os.makedirs(Config.TRAINING_DATA_DIR, exist_ok=True)
    os.makedirs(Config.TESTING_DATA_DIR, exist_ok=True)
    os.makedirs(Config.RESULTS_DIR, exist_ok=True)

    # Check for training data
    training_files = [
        f for f in os.listdir(Config.TRAINING_DATA_DIR)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]

    if not training_files:
        print('ERROR: No training data found in', Config.TRAINING_DATA_DIR)
        print('Please add student photos with naming format:')
        print('  student_001.jpg, student_002_Alice.jpg, etc.')
        sys.exit(1)

    tester = CoreSystemTest()
    tester.run_all_tests()
