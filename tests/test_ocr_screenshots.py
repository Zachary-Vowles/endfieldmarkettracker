"""
Test OCR accuracy against real screenshot data
Outputs debug images with drawn ROIs to verify coordinates.
"""
import pytest
import cv2
import os
import numpy as np
from src.core.ocr_engine import OCREngine
from src.core.data_extractor import DataExtractor
from src.utils.constants import DEFAULT_ROIS

# Helper directories
TEST_IMG_DIR = os.path.join(os.path.dirname(__file__), 'images')
DEBUG_OUT_DIR = os.path.join(os.path.dirname(__file__), 'debug_output')

def load_image(filename):
    path = os.path.join(TEST_IMG_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(f"Test image {filename} not found in {TEST_IMG_DIR}")
    return cv2.imread(path)

def save_debug_image(img, rois, output_filename):
    """Draws ROIs on the image and saves it for visual inspection."""
    os.makedirs(DEBUG_OUT_DIR, exist_ok=True)
    debug_img = img.copy()
    
    print("\n--- Current DEFAULT_ROIS ---")
    for name, roi in rois.items():
        print(f"{name}: {roi}")
        x, y, w, h = roi['x'], roi['y'], roi['w'], roi['h']
        
        # Draw green rectangle
        cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Put text label slightly above the rectangle
        cv2.putText(debug_img, name, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
    out_path = os.path.join(DEBUG_OUT_DIR, output_filename)
    cv2.imwrite(out_path, debug_img)
    print(f"Saved visual debug image to: {out_path}")
    print("----------------------------\n")

def test_screenshot_1_musbeast():
    """
    Test 'test_screenshot_1.png' (Musbeast Scrimshaw Dangles)
    """
    img = load_image("test_screenshot_1.png")
    
    # OUTPUT DEBUG IMAGE
    save_debug_image(img, DEFAULT_ROIS, "debug_screenshot_1.png")
    
    # 1. Extraction
    engine = OCREngine(use_gpu=False)
    results = engine.extract_prices(img, DEFAULT_ROIS)
    
    # 2. Processing
    extractor = DataExtractor()
    data = extractor.process_ocr_results(results)
    
    print(f"\nScreenshot 1 Extracted Data: {data}")

    assert data is not None
    assert "Musbeast" in data.name
    assert data.local_price == 1446
    assert data.average_cost == 1067
    assert data.quantity_owned == 138
    
    # Friend price should be None on this screen
    assert data.friend_price is None

def test_screenshot_2_friend_price():
    """
    Test 'test_screenshot_2.png' (Friend's Price Screen)
    """
    img = load_image("test_screenshot_2.png")
    
    # OUTPUT DEBUG IMAGE
    save_debug_image(img, DEFAULT_ROIS, "debug_screenshot_2.png")
    
    engine = OCREngine(use_gpu=False)
    results = engine.extract_prices(img, DEFAULT_ROIS)
    
    extractor = DataExtractor()
    data = extractor.process_ocr_results(results)
    
    print(f"\nScreenshot 2 Extracted Data: {data}")

    assert data is not None
    
    # Visible top price is 3680
    assert data.friend_price == 3680
    assert data.friend_price < 9000