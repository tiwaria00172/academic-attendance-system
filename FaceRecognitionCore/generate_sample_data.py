"""
Generate sample test data using synthetic face images.
Downloads sample face images from the internet for testing.

Run this ONCE to create sample data if you don't have your own photos.
"""

import os
import sys
import urllib.request
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config


def generate_synthetic_faces(output_dir, count=10):
    """
    Generate synthetic face-like images for testing.
    These are NOT real faces - they are colored rectangles with 
    oval shapes to simulate face-like images so the pipeline 
    can be tested structurally.
    
    For real testing, replace these with actual face photos.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Generating {count} synthetic test images in {output_dir}...")
    print("NOTE: These are placeholder images. Replace with real face photos")
    print("      for meaningful face recognition testing.\n")
    
    names = [
        'Alice', 'Bob', 'Charlie', 'Diana', 'Eve',
        'Frank', 'Grace', 'Hank', 'Iris', 'Jack',
        'Karen', 'Leo', 'Mona', 'Nick', 'Olivia'
    ]
    
    for i in range(min(count, len(names))):
        # Create a 400x400 image with a face-like oval
        img = np.ones((400, 400, 3), dtype=np.uint8) * 200  # Light gray bg
        
        # Add some variation per "student"
        np.random.seed(i + 42)  # Deterministic
        bg_color = np.random.randint(150, 230, 3).tolist()
        face_color = np.random.randint(180, 240, 3).tolist()
        
        # Background
        img[:, :] = bg_color
        
        # Draw face oval
        center = (200, 180)
        axes = (80, 100)
        cv2.ellipse(img, center, axes, 0, 0, 360, face_color, -1)
        
        # Draw eyes
        eye_color = (50, 50, 50)
        cv2.circle(img, (170, 160), 8, eye_color, -1)
        cv2.circle(img, (230, 160), 8, eye_color, -1)
        
        # Draw mouth
        cv2.ellipse(img, (200, 210), (25, 10), 0, 0, 180, eye_color, 2)
        
        # Draw nose
        cv2.line(img, (200, 170), (200, 195), eye_color, 2)
        
        student_id = f'{i+1:03d}'
        filename = f'student_{student_id}_{names[i]}.jpg'
        filepath = os.path.join(output_dir, filename)
        
        cv2.imwrite(filepath, img)
        print(f"  Created: {filename}")
    
    print(f"\nGenerated {min(count, len(names))} images.")
    print("IMPORTANT: Replace these with REAL face photos for actual testing!")


def try_download_lfw_samples(output_dir, count=10):
    """
    Try to download real face images from Labeled Faces in the Wild (LFW).
    Falls back to synthetic if download fails.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # LFW sample URLs (public domain face images)
    lfw_base = "http://vis-www.cs.umass.edu/lfw/images"
    
    # These are well-known public figures with multiple photos in LFW
    sample_people = [
        ("George_W_Bush", "George_W_Bush_0001.jpg"),
        ("Colin_Powell", "Colin_Powell_0001.jpg"),
        ("Tony_Blair", "Tony_Blair_0001.jpg"),
        ("Donald_Rumsfeld", "Donald_Rumsfeld_0001.jpg"),
        ("Gerhard_Schroeder", "Gerhard_Schroeder_0001.jpg"),
    ]
    
    downloaded = 0
    for name, filename in sample_people[:count]:
        url = f"{lfw_base}/{name}/{filename}"
        output_name = f"student_{downloaded+1:03d}_{name.replace('_', '')}.jpg"
        output_path = os.path.join(output_dir, output_name)
        
        try:
            print(f"  Downloading: {url}")
            urllib.request.urlretrieve(url, output_path)
            downloaded += 1
            print(f"    -> Saved as: {output_name}")
        except Exception as e:
            print(f"    -> Failed: {e}")
    
    return downloaded


if __name__ == '__main__':
    training_dir = Config.TRAINING_DATA_DIR
    testing_dir = Config.TESTING_DATA_DIR
    
    print("=" * 60)
    print("SAMPLE DATA GENERATOR")
    print("=" * 60)
    
    # Check if data already exists
    if os.path.exists(training_dir) and os.listdir(training_dir):
        print(f"\nTraining data already exists in {training_dir}")
        response = input("Overwrite? (y/n): ").strip().lower()
        if response != 'y':
            print("Skipping training data generation.")
            sys.exit(0)
    
    print("\nAttempting to download real face images from LFW...")
    downloaded = try_download_lfw_samples(training_dir, count=10)
    
    if downloaded < 3:
        print(f"\nOnly downloaded {downloaded} images. Generating synthetic data...")
        generate_synthetic_faces(training_dir, count=10)
    else:
        print(f"\nSuccessfully downloaded {downloaded} face images.")
    
    # Create empty testing dir
    os.makedirs(testing_dir, exist_ok=True)
    
    print(f"\nDirectories created:")
    print(f"  Training: {training_dir}")
    print(f"  Testing:  {testing_dir}")
    print(f"\nNext step: python test_core.py")
