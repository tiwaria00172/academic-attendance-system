"""
Core Face Recognition Service Wrapper
Bridges the existing core system with the Flask web layer.
The core modules (config, image_processor, face_recognition_engine,
face_matcher, data_loader) are UNCHANGED — this wrapper only CALLS them.
Includes Real-World Adaptive Recovery for challenging/small photos.
"""
import os
import sys
import numpy as np

# Ensure core modules are importable (FaceRecognitionCore root directory)
_core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if _core_dir not in sys.path:
    sys.path.insert(0, _core_dir)

from config import Config
from face_recognition_engine import FaceRecognitionEngine
from face_matcher import FaceMatcher
from data_loader import StudentDatabase


class CoreFaceRecognitionService:
    """High-level service used by Flask routes with Real-World Adaptive Recovery."""

    def __init__(self):
        self.engine = FaceRecognitionEngine()
        self.matcher = FaceMatcher()
        self.db_loader = StudentDatabase()
        self.student_database = {}
        self._load_student_database()

    # ── adaptive recovery helper ─────────────────────────────────
    def _adaptive_extract(self, photo_path):
        """
        Real-world adaptive recovery pipeline.
        When standard 1x scale detection fails on real-world photos (small faces,
        webcam captures, group shots, uncropped images), progressively upsample
        to find and encode the face without modifying the baseline core engine.
        """
        import face_recognition
        try:
            img = face_recognition.load_image_file(photo_path)

            # Fast fail for completely blank/solid images (like mock webcams)
            if np.std(img) < 5:
                print(f'[ADAPTIVE] Fast fail for blank image: {photo_path}')
                return None

            for scale in [2, 3]:
                locs = face_recognition.face_locations(img, number_of_times_to_upsample=scale, model='hog')
                if locs:
                    if len(locs) > 1:
                        areas = [(b - t) * (r - l) for (t, r, b, l) in locs]
                        locs = [locs[int(np.argmax(areas))]]
                    encs = face_recognition.face_encodings(img, locs, num_jitters=1)
                    if encs:
                        return np.array(encs[0], dtype=np.float64)
        except Exception as exc:
            print(f'[ADAPTIVE] Recovery failed for {photo_path}: {exc}')
        return None

    # ── bootstrap ────────────────────────────────────────────────
    def _load_student_database(self):
        try:
            training_dir = Config.TRAINING_DATA_DIR
            os.makedirs(training_dir, exist_ok=True)
            if any(f.lower().endswith(('.jpg', '.jpeg', '.png'))
                   for f in os.listdir(training_dir)):
                self.db_loader.load_students_from_folder(training_dir)
                self.student_database = self.db_loader.get_database()
                print(f'[CORE] Baseline loaded {len(self.student_database)} students')

                # Real-World Adaptive Recovery Pass for any photos missed by standard 1x detection
                photo_files = sorted([
                    f for f in os.listdir(training_dir)
                    if f.lower().endswith(('.jpg', '.jpeg', '.png'))
                ])
                for fname in photo_files:
                    info = self.db_loader._parse_filename(fname)
                    sid = info['id']
                    if sid not in self.student_database:
                        fpath = os.path.join(training_dir, fname)
                        print(f'[ADAPTIVE] Attempting real-world recovery for {fname}...')
                        enc = self._adaptive_extract(fpath)
                        if enc is not None:
                            self.student_database[sid] = {
                                'encoding': enc,
                                'name': info['name'],
                                'roll_number': info['roll_number'],
                                'photo_path': fpath
                            }
                            print(f'  [RECOVERED] {info["name"]} ({sid}) via multi-scale upsampling')

                print(f'[CORE] Final database: {len(self.student_database)} students ready')
            else:
                print('[CORE] No training images found — database empty')
        except Exception as exc:
            print(f'[CORE] Error loading student DB: {exc}')

    def reload_database(self):
        """Re-scan training folder (called after new photos are added)."""
        self.db_loader = StudentDatabase()
        self._load_student_database()

    # ── main pipeline ────────────────────────────────────────────
    def process_classroom_photos(self, photo_paths, classroom_id):
        all_matches = {
            'auto_marked': [],
            'needs_confirmation': [],
            'not_found': [],
        }
        total_detected = 0

        for photo_path in photo_paths:
            try:
                result = self.engine.extract_all_face_encodings(photo_path)
                if not result['success'] or result.get('face_count', 0) == 0:
                    # Adaptive multi-scale fallback for class photos with small/distant faces
                    import face_recognition
                    img = face_recognition.load_image_file(photo_path)
                    for scale in [2, 3]:
                        locs = face_recognition.face_locations(img, number_of_times_to_upsample=scale, model='hog')
                        if locs:
                            encs = face_recognition.face_encodings(img, locs, num_jitters=1)
                            if encs:
                                result = {
                                    'success': True,
                                    'face_count': len(encs),
                                    'encodings': [np.array(e, dtype=np.float64) for e in encs]
                                }
                                print(f'[ADAPTIVE] Recovered {len(encs)} face(s) in class photo at upsample scale {scale}')
                                break

                if not result['success']:
                    print(f'[CORE] Skip {photo_path}: {result.get("error", "Unknown error")}')
                    continue

                total_detected += result['face_count']
                matches = self.matcher.match_all_faces(
                    result['encodings'], self.student_database
                )
                all_matches['auto_marked'].extend(matches['auto_marked'])
                all_matches['needs_confirmation'].extend(matches['needs_confirmation'])
                all_matches['not_found'].extend(matches['not_found'])
            except Exception as exc:
                print(f'[CORE] Error: {exc}')

        # ── Determine which student IDs were detected ─────────────
        detected_ids = set()
        for m in all_matches['auto_marked']:
            detected_ids.add(m.get('student_id'))
        for m in all_matches['needs_confirmation']:
            bm = m.get('best_match', {})
            if bm:
                detected_ids.add(bm.get('student_id'))

        detected_rolls = set(str(rid).strip().lower() for rid in detected_ids if rid)

        # ── Fetch classroom enrollment roster from SQL ─────────────
        from app.models.classroom import Classroom
        classroom = Classroom.query.get(classroom_id)
        enrolled_students = list(classroom.students) if classroom else []
        has_enrollment = len(enrolled_students) > 0

        if has_enrollment:
            # ── ROSTERED MODE ──────────────────────────────────────
            # Classroom has enrolled students.  Only show matches for
            # students on the roster and mark all others absent.
            enrolled_rolls = set(str(s.roll_number).strip().lower() for s in enrolled_students)

            filtered_auto_marked = []
            for m in all_matches['auto_marked']:
                roll = m.get('roll_number') or m.get('student_id')
                if roll and str(roll).strip().lower() in enrolled_rolls:
                    filtered_auto_marked.append(m)

            filtered_needs_confirmation = []
            for m in all_matches['needs_confirmation']:
                bm = m.get('best_match', {})
                if bm:
                    roll = bm.get('roll_number') or bm.get('student_id')
                    if roll and str(roll).strip().lower() in enrolled_rolls:
                        filtered_needs_confirmation.append(m)

            all_matches['auto_marked'] = filtered_auto_marked
            all_matches['needs_confirmation'] = filtered_needs_confirmation

            # Enrolled students not detected → absent
            absent = []
            for s in enrolled_students:
                roll = str(s.roll_number).strip().lower()
                if roll not in detected_rolls:
                    absent.append({
                        'student_id': s.roll_number,
                        'name': s.name,
                        'roll_number': s.roll_number,
                    })

        else:
            # ── OPEN / UNROSTERED MODE ─────────────────────────────
            # Classroom has NO enrolled students yet (fresh / unset up).
            # Fall back to the global face-DB: show all detected matches
            # as-is so the teacher can still use the system immediately.
            # Students in the face DB who were not detected → absent.
            absent = [
                {
                    'student_id': sid,
                    'name': info['name'],
                    'roll_number': info.get('roll_number', sid),
                }
                for sid, info in self.student_database.items()
                if str(sid).strip().lower() not in detected_rolls
            ]

        return {
            'classroom_id': classroom_id,
            'total_faces_detected': total_detected,
            'matches': all_matches,
            'absent_students': absent,
            'enrollment_mode': 'rostered' if has_enrollment else 'open',
        }

    def extract_single_encoding(self, photo_path):
        """Extract encoding for a single student reference photo."""
        enc = self.engine.extract_student_encoding(photo_path)
        if enc is None:
            print(f'[ADAPTIVE] Standard extraction failed for {photo_path}, trying adaptive recovery...')
            enc = self._adaptive_extract(photo_path)
        return enc
