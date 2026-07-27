"""
Face Recognition Core System - Image Processor
================================================
Deterministic image preprocessing for face recognition.
Always applies the same steps in the same order.
"""

import cv2
import numpy as np
from config import Config
from PIL import Image


class ImageProcessor:
    """
    Preprocess images for face recognition.
    Deterministic: Always performs the same steps in the same order.
    """

    def __init__(self):
        self.config = Config

    # ─── Image Loading ───────────────────────────────────────────────────

    def load_image(self, image_path):
        """
        Load image from disk.

        Args:
            image_path: Path to image file (JPG/PNG)

        Returns:
            np.ndarray: Image in BGR format (OpenCV standard)

        Raises:
            ValueError: If image cannot be loaded or format is wrong
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f'Cannot read image: {image_path}')

            # Verify it's actually a color image
            if len(image.shape) < 3 or image.shape[2] != 3:
                raise ValueError(
                    f'Image must be RGB/BGR with 3 channels, '
                    f'got shape {image.shape}'
                )

            return image

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f'Error loading image {image_path}: {str(e)}')

    # ─── Quality Checks ─────────────────────────────────────────────────

    def check_resolution(self, image):
        """
        Check if image has minimum resolution.

        Args:
            image: np.ndarray image

        Returns:
            bool: True if acceptable, False if too small
        """
        height, width = image.shape[:2]
        min_h, min_w = self.config.IMAGE_MIN_DIMENSION

        return width >= min_w and height >= min_h

    def resize_image(self, image):
        """
        Resize image to max dimension (for faster processing).
        ALWAYS applied - never skipped.

        Args:
            image: Input image (BGR)

        Returns:
            np.ndarray: Resized image (or original if already small enough)
        """
        height, width = image.shape[:2]

        if max(height, width) > self.config.IMAGE_MAX_DIMENSION:
            scale = self.config.IMAGE_MAX_DIMENSION / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height),
                               interpolation=cv2.INTER_AREA)

        return image

    def check_brightness(self, image):
        """
        Check if image brightness is acceptable.

        Args:
            image: BGR image

        Returns:
            tuple: (is_acceptable, brightness_value, message)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        brightness = float(np.mean(gray))

        if brightness < self.config.BRIGHTNESS_MIN:
            return False, brightness, 'Too dark'
        if brightness > self.config.BRIGHTNESS_MAX:
            return False, brightness, 'Too bright'

        return True, brightness, 'Good brightness'

    def check_blur(self, image):
        """
        Check image sharpness using Laplacian variance.
        Low variance = blurry, high variance = sharp.

        Args:
            image: BGR image

        Returns:
            tuple: (is_acceptable, blur_score, message)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        blur_score = float(laplacian.var())

        if blur_score < self.config.BLUR_THRESHOLD:
            return False, blur_score, 'Too blurry'

        return True, blur_score, 'Good sharpness'

    def check_contrast(self, image):
        """
        Check image contrast using standard deviation.

        Args:
            image: BGR image

        Returns:
            tuple: (is_acceptable, contrast_value, message)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        contrast = float(np.std(gray))

        if contrast < self.config.CONTRAST_MIN:
            return False, contrast, 'Low contrast'

        return True, contrast, 'Good contrast'

    def check_lighting_uniformity(self, image):
        """
        Check if lighting is uniform across image.
        Divides into 4 quadrants and checks brightness variance.

        Args:
            image: BGR image

        Returns:
            tuple: (is_acceptable, variance, message)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # Split into 4 quadrants
        quadrants = [
            gray[0:h // 2, 0:w // 2],       # Top-left
            gray[0:h // 2, w // 2:w],        # Top-right
            gray[h // 2:h, 0:w // 2],        # Bottom-left
            gray[h // 2:h, w // 2:w]         # Bottom-right
        ]

        brightness_levels = [float(np.mean(q)) for q in quadrants]
        variance = float(np.var(brightness_levels))

        if variance > self.config.LIGHTING_VARIANCE_MAX:
            return False, variance, 'Uneven lighting'

        return True, variance, 'Even lighting'

    # ─── Master Quality Check ────────────────────────────────────────────

    def check_photo_quality(self, image_path):
        """
        MASTER QUALITY CHECK - Run all quality checks on an image.

        Args:
            image_path: Path to image file

        Returns:
            dict: Quality assessment with keys:
                - image: the loaded image (BGR)
                - quality_score: 0-100
                - issues: list of issue strings
                - acceptable: bool
                - brightness, blur_score, contrast, lighting_variance
        """
        image = self.load_image(image_path)

        results = {
            'image': image,
            'quality_score': 0,
            'issues': [],
            'acceptable': False
        }

        # Check 1: Resolution
        resolution_ok = self.check_resolution(image)
        if not resolution_ok:
            results['issues'].append('Resolution too low')

        # Check 2: Brightness
        bright_ok, brightness, bright_msg = self.check_brightness(image)
        results['brightness'] = brightness
        if not bright_ok:
            results['issues'].append(bright_msg)

        # Check 3: Blur
        blur_ok, blur_score, blur_msg = self.check_blur(image)
        results['blur_score'] = blur_score
        if not blur_ok:
            results['issues'].append(blur_msg)

        # Check 4: Contrast
        contrast_ok, contrast, contrast_msg = self.check_contrast(image)
        results['contrast'] = contrast
        if not contrast_ok:
            results['issues'].append(contrast_msg)

        # Check 5: Lighting uniformity
        light_ok, variance, light_msg = self.check_lighting_uniformity(image)
        results['lighting_variance'] = variance
        if not light_ok:
            results['issues'].append(light_msg)

        # Calculate quality score (0-100)
        checks = [resolution_ok, bright_ok, blur_ok, contrast_ok, light_ok]
        checks_passed = sum(checks)
        total_checks = len(checks)

        results['quality_score'] = (checks_passed / total_checks) * 100
        results['acceptable'] = results['quality_score'] >= self.config.MIN_QUALITY_SCORE

        return results

    # ─── Deterministic Preprocessing Pipeline ────────────────────────────

    def preprocess_image(self, image_path):
        """
        DETERMINISTIC PREPROCESSING - Always same steps in same order.

        Pipeline:
            1. Load image & check quality
            2. Resize if needed
            3. Apply CLAHE contrast enhancement

        Args:
            image_path: Path to image file

        Returns:
            tuple: (preprocessed_image, quality_info)

        Raises:
            ValueError: If image quality is too poor to process
        """
        # Step 1: Quality check
        quality_info = self.check_photo_quality(image_path)

        if not quality_info['acceptable']:
            raise ValueError(
                f'Image quality unacceptable. '
                f'Score: {quality_info["quality_score"]:.1f}/100. '
                f'Issues: {quality_info["issues"]}'
            )

        image = quality_info['image']

        # Step 2: Resize ALWAYS (no-op if already small enough)
        image = self.resize_image(image)

        # Step 3: Apply CLAHE to L channel (ALWAYS, never skip)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)

        clahe = cv2.createCLAHE(
            clipLimit=self.config.CLAHE_CLIP_LIMIT,
            tileGridSize=(
                self.config.CLAHE_TILE_SIZE,
                self.config.CLAHE_TILE_SIZE
            )
        )
        l_enhanced = clahe.apply(l_channel)

        lab_enhanced = cv2.merge([l_enhanced, a_channel, b_channel])
        image_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

        return image_enhanced, quality_info
