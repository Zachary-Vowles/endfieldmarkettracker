"""
Tests for Endfield Market Tracker
OCR + Core Logic Tests
"""

import pytest
import numpy as np
import cv2
from pathlib import Path


# --------------------------------------------------
# CALIBRATED ROIs FOR 2560x1440 FULLSCREEN
# --------------------------------------------------

DEFAULT_ROIS = {
    'product_name':   {'x': 961,  'y': 366,  'w': 705, 'h': 54},
    'local_price':    {'x': 1922, 'y': 1017, 'w': 121, 'h': 64},
    'average_cost':   {'x': 688,  'y': 856,  'w': 150, 'h': 50},
    'quantity_owned': {'x': 210,  'y': 585,  'w': 210, 'h': 50},
    'friend_price':   {'x': 710,  'y': 804,  'w': 132, 'h': 44}
}


# --------------------------------------------------
# Helper: Load Test Image
# --------------------------------------------------

def load_test_image(filename: str) -> np.ndarray:
    """Safely load image from tests/images folder"""
    test_dir = Path(__file__).parent
    image_path = test_dir / "images" / filename

    assert image_path.exists(), f"Test image not found: {image_path}"

    img = cv2.imread(str(image_path))
    assert img is not None, f"Failed to load image: {image_path}"

    return img


# --------------------------------------------------
# BASIC PREPROCESS TEST
# --------------------------------------------------

def test_ocr_preprocessing():
    from src.core.ocr_engine import OCREngine

    engine = OCREngine(use_gpu=False)

    img = load_test_image("test_screenshot_1.png")
    processed = engine.preprocess_image(img)

    assert processed is not None
    assert len(processed.shape) == 2
    assert processed.dtype == np.uint8


# --------------------------------------------------
# FULL ROI OCR EXTRACTION TEST
# --------------------------------------------------

@pytest.mark.integration
def test_extract_all_rois_screenshot_1():
    """Test extracting all calibrated ROIs from screenshot 1"""

    from src.core.ocr_engine import OCREngine

    engine = OCREngine(use_gpu=False)
    img = load_test_image("test_screenshot_1.png")

    # Verify correct resolution
    assert img.shape[1] == 2560
    assert img.shape[0] == 1440

    results = engine.extract_prices(img, DEFAULT_ROIS)

    assert isinstance(results, dict)

    for key in DEFAULT_ROIS.keys():
        assert key in results

    # Basic sanity checks (not strict text matching because OCR varies)
    assert results["product_name"] is None or isinstance(results["product_name"], str)
    assert results["local_price"] is None or isinstance(results["local_price"], int)
    assert results["average_cost"] is None or isinstance(results["average_cost"], int)
    assert results["quantity_owned"] is None or isinstance(results["quantity_owned"], int)
    assert results["friend_price"] is None or isinstance(results["friend_price"], int)


# --------------------------------------------------
# SECOND SCREENSHOT TEST
# --------------------------------------------------

@pytest.mark.integration
def test_extract_all_rois_screenshot_2():
    """Test extracting all calibrated ROIs from screenshot 2"""

    from src.core.ocr_engine import OCREngine

    engine = OCREngine(use_gpu=False)
    img = load_test_image("test_screenshot_2.png")

    assert img.shape[1] == 2560
    assert img.shape[0] == 1440

    results = engine.extract_prices(img, DEFAULT_ROIS)

    assert isinstance(results, dict)

    for key in DEFAULT_ROIS.keys():
        assert key in results


# --------------------------------------------------
# NUMBER EXTRACTION DIRECT ROI TEST
# --------------------------------------------------

@pytest.mark.integration
def test_direct_number_extraction():
    """Test extracting just the local_price ROI directly"""

    from src.core.ocr_engine import OCREngine

    engine = OCREngine(use_gpu=False)
    img = load_test_image("test_screenshot_1.png")

    roi = DEFAULT_ROIS["local_price"]

    region = img[
        roi["y"]:roi["y"] + roi["h"],
        roi["x"]:roi["x"] + roi["w"]
    ]

    number = engine.extract_number(region)

    assert number is None or isinstance(number, int)


# --------------------------------------------------
# FAST UNIT TESTS (NO OCR)
# --------------------------------------------------

def test_price_extraction():
    from src.core.data_extractor import DataExtractor

    extractor = DataExtractor()

    assert extractor.extract_price("1,234 HZ") == 1234
    assert extractor.extract_price("5678") == 5678
    assert extractor.extract_price("Price: 9,999") == 9999
    assert extractor.extract_price("") is None


def test_percentage_extraction():
    from src.core.data_extractor import DataExtractor

    extractor = DataExtractor()

    assert extractor.extract_percentage("+40.5%") == 40.5
    assert extractor.extract_percentage("-15.2%") == -15.2
    assert extractor.extract_percentage("80.9%") == 80.9
    assert extractor.extract_percentage("") is None


if __name__ == "__main__":
    pytest.main(["-v"])