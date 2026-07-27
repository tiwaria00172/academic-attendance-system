"""
Download REAL face images from LFW (Labeled Faces in the Wild) public dataset
to prove the system works end-to-end with actual human faces.
"""

import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config


# LFW public face images - these are real face photos of public figures
LFW_SAMPLES = [
    ("George_W_Bush", "George_W_Bush_0001.jpg", "001", "George Bush"),
    ("George_W_Bush", "George_W_Bush_0002.jpg", "001b", "George Bush Alt"),
    ("Colin_Powell", "Colin_Powell_0001.jpg", "002", "Colin Powell"),
    ("Colin_Powell", "Colin_Powell_0002.jpg", "002b", "Colin Powell Alt"),
    ("Tony_Blair", "Tony_Blair_0001.jpg", "003", "Tony Blair"),
    ("Tony_Blair", "Tony_Blair_0002.jpg", "003b", "Tony Blair Alt"),
    ("Donald_Rumsfeld", "Donald_Rumsfeld_0001.jpg", "004", "Donald Rumsfeld"),
    ("Gerhard_Schroeder", "Gerhard_Schroeder_0001.jpg", "005", "Gerhard Schroeder"),
    ("Ariel_Sharon", "Ariel_Sharon_0001.jpg", "006", "Ariel Sharon"),
    ("Hugo_Chavez", "Hugo_Chavez_0001.jpg", "007", "Hugo Chavez"),
    ("Junichiro_Koizumi", "Junichiro_Koizumi_0001.jpg", "008", "Junichiro Koizumi"),
    ("Jean_Chretien", "Jean_Chretien_0001.jpg", "009", "Jean Chretien"),
    ("John_Ashcroft", "John_Ashcroft_0001.jpg", "010", "John Ashcroft"),
]

# These will go to testing/ - second photos of same people to test matching
LFW_TEST_SAMPLES = [
    ("George_W_Bush", "George_W_Bush_0003.jpg", "test_bush"),
    ("Colin_Powell", "Colin_Powell_0003.jpg", "test_powell"),
    ("Tony_Blair", "Tony_Blair_0003.jpg", "test_blair"),
]


def download_lfw_images():
    base_url = "http://vis-www.cs.umass.edu/lfw/images"

    # Download training images
    training_dir = Config.TRAINING_DATA_DIR
    os.makedirs(training_dir, exist_ok=True)

    print("=" * 60)
    print("DOWNLOADING REAL FACE IMAGES FROM LFW DATASET")
    print("=" * 60)

    print(f"\n--- Training Images ({training_dir}) ---")
    downloaded_training = 0
    for person_dir, filename, student_id, name in LFW_SAMPLES:
        url = f"{base_url}/{person_dir}/{filename}"
        safe_name = name.replace(" ", "")
        output_name = f"student_{student_id}_{safe_name}.jpg"
        output_path = os.path.join(training_dir, output_name)

        if os.path.exists(output_path):
            print(f"  [SKIP] {output_name} (already exists)")
            downloaded_training += 1
            continue

        try:
            print(f"  Downloading: {filename} ...", end=" ")
            urllib.request.urlretrieve(url, output_path)
            
            # Verify file size
            size = os.path.getsize(output_path)
            if size < 1000:
                os.remove(output_path)
                print(f"FAILED (too small: {size} bytes)")
                continue
            
            print(f"OK ({size:,} bytes) -> {output_name}")
            downloaded_training += 1
        except Exception as e:
            print(f"FAILED ({e})")

    # Download test images
    testing_dir = Config.TESTING_DATA_DIR
    os.makedirs(testing_dir, exist_ok=True)

    print(f"\n--- Testing Images ({testing_dir}) ---")
    downloaded_testing = 0
    for person_dir, filename, test_id in LFW_TEST_SAMPLES:
        url = f"{base_url}/{person_dir}/{filename}"
        output_name = f"class_photo_{test_id}.jpg"
        output_path = os.path.join(testing_dir, output_name)

        if os.path.exists(output_path):
            print(f"  [SKIP] {output_name} (already exists)")
            downloaded_testing += 1
            continue

        try:
            print(f"  Downloading: {filename} ...", end=" ")
            urllib.request.urlretrieve(url, output_path)
            size = os.path.getsize(output_path)
            if size < 1000:
                os.remove(output_path)
                print(f"FAILED (too small)")
                continue
            print(f"OK ({size:,} bytes) -> {output_name}")
            downloaded_testing += 1
        except Exception as e:
            print(f"FAILED ({e})")

    print(f"\n{'=' * 60}")
    print(f"DOWNLOAD COMPLETE")
    print(f"  Training: {downloaded_training} images")
    print(f"  Testing:  {downloaded_testing} images")
    print(f"{'=' * 60}")

    return downloaded_training, downloaded_testing


if __name__ == "__main__":
    t, te = download_lfw_images()
    if t >= 3:
        print(f"\nReady to test! Run:  python test_core.py")
    else:
        print(f"\nNot enough images downloaded. Check your internet connection.")
