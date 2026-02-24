"""
Endfield Market Tracker - Main Entry Point
"""
try:
    from loguru import logger
except Exception:
    import logging
    logger = logging.getLogger("emt")
    logging.basicConfig(level=logging.INFO)
    logger.error("loguru not available; falling back to stdlib logging. Install with: pip install loguru")
    # optionally raise a clearer error or exit here

import time
import sys
import os
import logging
logging.basicConfig(level=logging.DEBUG)
logger.add("debug_log.txt", rotation="500 MB", level="DEBUG")
# Configure logger to save to a file and show in console
logger.add("debug_log.txt", rotation="500 MB")

def diagnostic_ocr_step(image):
    start = time.time()
    # Logic here...
    logger.info(f"Capture took: {time.time() - start:.4f}s")

def check_dependencies():
    """Check that all required dependencies are installed"""
    missing = []
    
    try:
        import PyQt6
    except ImportError:
        missing.append("PyQt6>=6.4.0")
    
    try:
        import cv2
    except ImportError:
        missing.append("opencv-python>=4.8.0")
    
    try:
        import numpy
    except ImportError:
        missing.append("numpy>=1.24.0,<2.0.0")
    
    try:
        import easyocr
    except ImportError:
        missing.append("easyocr>=1.7.0 (requires torch)")
    
    try:
        import sqlalchemy
    except ImportError:
        missing.append("SQLAlchemy>=2.0.0")
    
    try:
        import pyqtgraph
    except ImportError:
        missing.append("pyqtgraph>=0.13.0")
    
    try:
        import mss
    except ImportError:
        missing.append("mss>=9.0.0")
    
    try:
        import appdirs
    except ImportError:
        missing.append("appdirs>=1.4.4")
    
    try:
        import PIL
    except ImportError:
        missing.append("Pillow>=10.0.0")
    
    if missing:
        print("=" * 70)
        print("ERROR: Missing required dependencies")
        print("=" * 70)
        print("\nThe following packages are missing:\n")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nTo install all dependencies, run:")
        print("\n  pip install -r requirements.txt")
        print("\nOr install individually:")
        print(f"\n  pip install {' '.join(missing)}")
        print("\n" + "=" * 70)
        return False
    
    return True

def check_gpu():
    """Check GPU availability for OCR"""
    try:
        import torch
        if torch.cuda.is_available():
            # Use ASCII instead of Unicode checkmark for Windows compatibility
            print(f"[OK] GPU detected: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print("[INFO] No GPU detected - OCR will use CPU (slower)")
            return False
    except ImportError:
        print("[INFO] PyTorch not installed - cannot check GPU")
        return False

# Add src to path (for development mode)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def main():
    """Main application entry point"""
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # GPU info (optional)
    check_gpu()
    
    # Now import the rest
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont

    from src.ui.main_window import MainWindow
    from src.utils.constants import COLORS

    print("\nStarting Endfield Market Tracker...")
    print("=" * 70)
    
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Endfield Market Tracker")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("EndfieldMarketTracker")
    
    # Set default font
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    print("[OK] Application started successfully")
    print("=" * 70)
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()