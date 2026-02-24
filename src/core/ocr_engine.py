"""
OCR Engine for reading text from game screenshots
Uses EasyOCR for text recognition
"""

import cv2
import numpy as np
from typing import Dict, Optional, Tuple
import easyocr
from loguru import logger

class OCREngine:
    """Handles OCR operations for price extraction"""
    
    def __init__(self, use_gpu: bool = True):
        """Initialize OCR engine"""
        self.reader = easyocr.Reader(
            ['en'],  # English only for now
            gpu=use_gpu,
            verbose=False
        )
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR accuracy"""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply thresholding to improve contrast
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Resize if too small (OCR works better with larger text)
        height, width = thresh.shape
        if height < 40:
            scale = 40 / height
            thresh = cv2.resize(thresh, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        return thresh
    
    def extract_text(self, image: np.ndarray, confidence_threshold: float = 0.8) -> str:
        """Extract text from image region"""
        processed = self.preprocess_image(image)
        
        results = self.reader.readtext(processed)
        
        if not results:
            return ""
        
        # Get the highest confidence result
        best_result = max(results, key=lambda x: x[2])
        text, confidence = best_result[1], best_result[2]
        
        if confidence < confidence_threshold:
            return ""
        
        return text.strip()
    
    def extract_number(self, image: np.ndarray, confidence_threshold: float = 0.8) -> Optional[int]:
        """Extract a number from image region"""
        text = self.extract_text(image, confidence_threshold)
        
        # Remove non-digit characters except comma and period
        cleaned = ''.join(c for c in text if c.isdigit() or c in ',.')
        cleaned = cleaned.replace(',', '').replace('.', '')
        
        try:
            return int(cleaned) if cleaned else None
        except ValueError:
            return None
    
    def extract_prices(self, screenshot: np.ndarray, rois: Dict) -> Dict:
        """Extract all prices from a screenshot using defined ROIs"""
        results = {}
        
        for key, roi in rois.items():
            x, y, w, h = roi['x'], roi['y'], roi['w'], roi['h']
            
            # Bounds check - make sure ROI is within screenshot
            if y+h > screenshot.shape[0] or x+w > screenshot.shape[1]:
                logger.warning(f"ROI {key} out of bounds: ({x},{y},{w},{h}) vs screenshot {screenshot.shape}")
                results[key] = None
                continue
            
            region = screenshot[y:y+h, x:x+w]
            
            if 'price' in key or 'cost' in key:
                value = self.extract_number(region)
                logger.debug(f"OCR {key}: extracted number = {value}")  # DEBUG
            else:
                value = self.extract_text(region)
                logger.debug(f"OCR {key}: extracted text = '{value}'")  # DEBUG
            
            results[key] = value
        
        logger.info(f"OCR Results: {results}")  # DEBUG - always show this
        return results