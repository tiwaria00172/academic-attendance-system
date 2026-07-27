"""
Flask Application Entry Point
Adds the core FaceRecognitionCore directory to Python path,
then starts the Flask development server.
"""
import sys
import os

# Add FaceRecognitionCore/ (parent) to path so core modules are importable
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
