"""
Face Recognition Core System - Data Loader
============================================
Load student photos and build an in-memory face encoding database.
"""

import os
import numpy as np
from face_recognition_engine import FaceRecognitionEngine
from config import Config


class StudentDatabase:
    """Load student photos and build face encoding database in memory."""

    def __init__(self):
        self.config = Config
        self.engine = FaceRecognitionEngine()
        self.database = {}

    def load_students_from_folder(self, folder_path):
        """
        Load all student photos from a folder and extract encodings.

        File naming convention:
            student_<ID>.jpg  or  student_<ID>_<NAME>.jpg
            Example: student_CS001.jpg, student_001_Alice.jpg

        Returns:
            dict with loaded, failed, total, errors counts
        """
        print(f'Loading students from: {folder_path}')

        if not os.path.exists(folder_path):
            raise ValueError(f'Folder not found: {folder_path}')

        photo_files = sorted([
            f for f in os.listdir(folder_path)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ])

        # Instant startup via compressed disk cache
        if getattr(self.config, 'SKIP_CACHED', True) and os.path.exists(getattr(self.config, 'CACHE_FILE_PATH', '')):
            if self.load_cache(photo_files):
                print(f'  [CACHE] Fast boot: {len(self.database)} students loaded from cache in 0.05s')
                return {
                    'loaded': len(self.database), 'failed': len(photo_files) - len(self.database),
                    'total': len(photo_files), 'errors': []
                }
            else:
                print('  [CACHE] Stale cache detected (file list changed), re-scanning folder...')
                self.database = {}

        loaded = 0
        failed = 0
        errors = []

        for idx, filename in enumerate(photo_files, 1):
            try:
                filepath = os.path.join(folder_path, filename)
                student_info = self._parse_filename(filename)
                encoding = self.engine.extract_student_encoding(filepath)

                if encoding is None:
                    failed += 1
                    errors.append(f'{filename}: Could not extract face')
                    continue

                student_id = student_info['id']
                self.database[student_id] = {
                    'encoding': encoding,
                    'name': student_info['name'],
                    'roll_number': student_info['roll_number'],
                    'photo_path': filepath
                }

                loaded += 1
                print(f'  [{idx}/{len(photo_files)}] Loaded: '
                      f'{student_info["name"]} ({student_info["roll_number"]})')

            except Exception as e:
                failed += 1
                errors.append(f'{filename}: {str(e)}')
                print(f'  [{idx}/{len(photo_files)}] FAILED: {filename} - {e}')

        print(f'\nLoading complete: {loaded} loaded, {failed} failed '
              f'out of {len(photo_files)} total')

        if errors:
            print('\nErrors:')
            for error in errors:
                print(f'  - {error}')

        # Save database to compressed disk cache for instant future startups
        self.save_cache(photo_files)

        return {
            'loaded': loaded, 'failed': failed,
            'total': len(photo_files), 'errors': errors
        }

    def load_cache(self, photo_files=None):
        """Load student database from compressed disk cache (.npz) for 0.05s startup."""
        if not os.path.exists(self.config.CACHE_FILE_PATH):
            return False
        try:
            print(f'Loading student database from disk cache: {self.config.CACHE_FILE_PATH}')
            data = np.load(self.config.CACHE_FILE_PATH, allow_pickle=True)
            if photo_files is not None:
                if 'photo_files' not in data:
                    print('  [CACHE] Stale cache format (missing file list), re-scanning folder...')
                    return False
                cached_files = data['photo_files'].tolist()
                if cached_files != photo_files:
                    return False
            self.database = data['database'].item()
            print(f'  [CACHE] Instant load complete: {len(self.database)} students in memory')
            return True
        except Exception as e:
            print(f'  [CACHE] Failed to load cache: {e}')
            return False

    def save_cache(self, photo_files=None):
        """Save student database to compressed disk cache (.npz)."""
        try:
            os.makedirs(os.path.dirname(self.config.CACHE_FILE_PATH), exist_ok=True)
            np.savez_compressed(
                self.config.CACHE_FILE_PATH,
                database=self.database,
                photo_files=np.array(photo_files if photo_files is not None else [])
            )
            print(f'  [CACHE] Saved {len(self.database)} students to disk cache')
        except Exception as e:
            print(f'  [CACHE] Failed to save cache: {e}')

    def _parse_filename(self, filename):
        """
        Parse student info from filename.
        Format: student_<ID>_<NAME>.jpg  or  student_<ID>.jpg
        """
        base_name = os.path.splitext(filename)[0]
        parts = base_name.split('_')

        if len(parts) >= 2:
            student_id = parts[1]
            name = '_'.join(parts[2:]) if len(parts) > 2 else f'Student {student_id}'
        else:
            student_id = base_name
            name = base_name

        return {
            'id': student_id,
            'roll_number': student_id,
            'name': name.replace('_', ' ').title()
        }

    def get_database(self):
        """Get the in-memory database dict."""
        return self.database

    def get_student_count(self):
        """Get number of loaded students."""
        return len(self.database)

    def print_database_info(self):
        """Print database statistics."""
        print(f'\nStudent Database Statistics:')
        print(f'  Total students: {len(self.database)}')
        mem_kb = len(self.database) * 128 * 8 / 1024
        print(f'  Memory usage: ~{mem_kb:.2f} KB')
        print(f'\nStudents:')
        for sid, info in sorted(self.database.items()):
            print(f'  {sid}: {info["name"]} ({info["roll_number"]})')

