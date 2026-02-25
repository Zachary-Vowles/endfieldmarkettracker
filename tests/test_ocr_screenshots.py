"""
Test OCR accuracy against real screenshot data
"""
import pytest
import cv2
import os
import numpy as np
from src.core.ocr_engine import OCREngine
from src.core.data_extractor import DataExtractor
from src.utils.constants import DEFAULT_ROIS

# Helper to find test images
TEST_IMG_DIR = os.path.join(os.path.dirname(__file__), 'images')

def load_image(filename):
    path = os.path.join(TEST_IMG_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(f"Test image {filename} not found in {TEST_IMG_DIR}")
    return cv2.imread(path)

def test_screenshot_1_musbeast():
    """
    Test 'test_screenshot_1.png' (Musbeast Scrimshaw Dangles)
    Visible Data:
    - Name: Musbeast Scrimshaw Dangles [pkg]
    - Local Price: 1446
    - Owned: 138
    - Avg Cost: 1067
    - Friend Price: None (This is the purchase screen)
    """
    img = load_image("test_screenshot_1.png")
    
    # 1. Extraction
    engine = OCREngine(use_gpu=False)
    results = engine.extract_prices(img, DEFAULT_ROIS)
    
    # 2. Processing
    extractor = DataExtractor()
    data = extractor.process_ocr_results(results)
    
    print(f"\nScreenshot 1 Data: {data}")

    assert data is not None
    assert "Musbeast" in data.name ##Does this mean it isn't getting the name from the actual image?
    assert data.local_price == 1446 
    assert data.average_cost == 1067
    assert data.quantity_owned == 138
    
    # Friend price should be None on this screen
    # If the OCR is picking up noise (like 9000+), the extractor filter should handle it
    assert data.friend_price is None

def test_screenshot_2_friend_price():
    """
    Test 'test_screenshot_2.png' (Friend's Price Screen)
    Visible Data:
    - Name: (Might be obscured or '1067' if ROI hits the top bar)
    - Friend Price: 3680 (Top row: Endministrator#01139)
    """
    img = load_image("test_screenshot_2.png")
    
    engine = OCREngine(use_gpu=False)
    results = engine.extract_prices(img, DEFAULT_ROIS)
    
    extractor = DataExtractor()
    data = extractor.process_ocr_results(results)
    
    print(f"\nScreenshot 2 Data: {data}")

    assert data is not None
    
    # The key metric here is the Friend Price
    # Visible top price is 3680
    assert data.friend_price == 3680
    
    # Ensure it didn't pick up the 'Vs Local' percentage as a price
    assert data.friend_price < 5000
   