"""
Face Recognition Core System - Configuration
=============================================
All configuration constants in ONE place. Never hardcode values elsewhere.
"""

import numpy as np
import os


class Config:
    """Face Recognition Configuration - All tunable parameters."""

    # ─── Paths ───────────────────────────────────────────────────────────
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TRAINING_DATA_DIR = os.environ.get('TRAINING_DATA_DIR', os.path.join(BASE_DIR, 'data', 'training'))
    TESTING_DATA_DIR = os.environ.get('TESTING_DATA_DIR', os.path.join(BASE_DIR, 'data', 'testing'))
    RESULTS_DIR = os.environ.get('RESULTS_DIR', os.path.join(BASE_DIR, 'results'))

    # ─── Face Recognition Thresholds ─────────────────────────────────────
    FACE_CONFIDENCE_AUTO = float(os.environ.get('FACE_CONFIDENCE_AUTO', 0.45))     # Auto-mark present threshold
    FACE_CONFIDENCE_MANUAL = float(os.environ.get('FACE_CONFIDENCE_MANUAL', 0.30)) # Needs confirmation threshold
    FACE_AMBIGUITY_THRESHOLD = float(os.environ.get('FACE_AMBIGUITY_THRESHOLD', 0.03)) # Ambiguity detection range

    # ─── Image Processing ────────────────────────────────────────────────
    FACE_DETECTION_MODEL = os.environ.get('FACE_DETECTION_MODEL', 'hog')           # 'hog' (CPU) or 'cnn' (GPU)
    IMAGE_MAX_DIMENSION = int(os.environ.get('IMAGE_MAX_DIMENSION', 1200))         # Resize limit in pixels
    IMAGE_MIN_DIMENSION = (100, 100)     # Minimum resolution check (height, width)

    # ─── CLAHE (Contrast Limited Adaptive Histogram Equalization) ────────
    CLAHE_CLIP_LIMIT = 2.0               # Contrast enhancement strength
    CLAHE_TILE_SIZE = 8                  # Tile grid size for CLAHE

    # ─── Photo Quality Checks ────────────────────────────────────────────
    BRIGHTNESS_MIN = 40                  # Too dark threshold (mean pixel value)
    BRIGHTNESS_MAX = 220                 # Too bright threshold
    BLUR_THRESHOLD = 20                  # Laplacian variance (low = blurry)
    CONTRAST_MIN = 20                    # Minimum standard deviation
    LIGHTING_VARIANCE_MAX = 800          # Quadrant brightness variance limit

    # ─── Face Detection Parameters ───────────────────────────────────────
    FACE_DETECTION_SCALE_FACTOR = 1.1    # Scale factor for cascade
    MIN_FACE_SIZE = (30, 30)             # Minimum face bounding box
    MAX_FACES_PER_IMAGE = 100            # Safety limit per image
    ENCODING_PRECISION = np.float64      # Encoding data type (64-bit for precision)

    # ─── Batch Processing & Caching ──────────────────────────────────────
    BATCH_SIZE = int(os.environ.get('BATCH_SIZE', 32))                             # Process N images per batch
    SKIP_CACHED = True                   # Skip already-encoded students
    CACHE_FILE_PATH = os.environ.get('CACHE_FILE_PATH', os.path.join(BASE_DIR, 'data', 'student_encodings_cache.npz'))

    # ─── Encoding Extraction & Multi-Template ────────────────────────────
    NUM_JITTERS = int(os.environ.get('NUM_JITTERS', 1))                            # 1 = fast, 10+ = more accurate
    MAX_TEMPLATES_PER_STUDENT = 5        # Support up to 5 reference photos per student
    UPSAMPLE_TRAINING = int(os.environ.get('UPSAMPLE_TRAINING', 2))                # Default zoom for reference photos
    UPSAMPLE_CLASSROOM = int(os.environ.get('UPSAMPLE_CLASSROOM', 1))              # Baseline zoom for classroom photos
    UPSAMPLE_MAX = int(os.environ.get('UPSAMPLE_MAX', 3))                          # Max fallback zoom

    # ─── Quality Score ───────────────────────────────────────────────────
    MIN_QUALITY_SCORE = 60               # Minimum quality score to accept (0-100)

