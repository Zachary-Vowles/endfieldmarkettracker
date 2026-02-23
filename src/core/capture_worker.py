"""
Capture Worker - Fully automated screen capture and OCR
No calibration needed - works out of the box at 2560x1440
"""

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, QMutex, QWaitCondition
from typing import Dict, Optional, List
import time
from loguru import logger
from collections import deque

from src.core.screen_capture import ScreenCapture
from src.core.ocr_engine import OCREngine
from src.core.data_extractor import DataExtractor, ProductData
from src.database.manager import DatabaseManager
from src.utils.constants import CAPTURE_SETTINGS, DEFAULT_ROIS, AUTO_DETECT

class CaptureWorker(QThread):
    """
    Automated capture worker that detects game screens and extracts prices.
    Uses 'Smart Scaling' to adjust 1440p coordinates to the actual window size.
    """
    
    # Signals
    product_captured = pyqtSignal(str, str, int, int, int, int, object)  # name, region, local, friend, owned, avg_cost
    status_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    capture_count = pyqtSignal(int) # Total products captured this session
    screenshot_captured = pyqtSignal(object, str)  # image, status
    
    def __init__(self, db_manager: DatabaseManager, monitor_idx: int = None):
        super().__init__()
        self.db_manager = db_manager
        self.monitor_idx = monitor_idx
        self.running = False
        self.session_id = None
        
        # Initialize components
        self.screen_capture = None
        self.ocr_engine = OCREngine(use_gpu=True)
        self.data_extractor = DataExtractor()
        
        # State tracking
        self.current_product = None
        self.last_prices = {}  
        self.last_log_time = 0
        self.capture_count_value = 0
        
        # Mutex for thread safety
        self.mutex = QMutex()
        
    def run(self):
        """Main capture loop"""
        self.running = True
        self.status_update.emit("Initializing capture system...")
        
        try:
            self.screen_capture = ScreenCapture()
            
            # Start database session
            self.session_id = self.db_manager.start_session()
            self.status_update.emit("[OK] Ready - Click through your goods in-game")
            
            while self.running:
                # 1. Capture the targeted game window
                screenshot = self.screen_capture.capture_full_screen()
                
                if screenshot is not None:
                    # 2. Run scaling and OCR
                    self._process_frame(screenshot)
                
                # Cap at configured FPS
                time.sleep(1 / CAPTURE_SETTINGS.get('fps', 10))
                
        except Exception as e:
            logger.error(f"Capture error: {e}")
            self.error_occurred.emit(f"Capture error: {str(e)}")
        finally:
            self._cleanup()
    
    def _process_frame(self, screenshot: np.ndarray):
        """Handles visual debugging and coordinate scaling."""
        h, w = screenshot.shape[:2]
        
        # SMART SCALING: Map 1440p (target) to actual window size
        scale_x = w / 2560
        scale_y = h / 1440
        
        # Create Debug View
        debug_img = screenshot.copy()
        scaled_rois = {}

        for name, roi in DEFAULT_ROIS.items():
            sx, sy = int(roi['x'] * scale_x), int(roi['y'] * scale_y)
            sw, sh = int(roi['w'] * scale_x), int(roi['h'] * scale_y)
            scaled_rois[name] = {'x': sx, 'y': sy, 'w': sw, 'h': sh}
            
            # Draw green boxes for calibration
            cv2.rectangle(debug_img, (sx, sy), (sx + sw, sy + sh), (0, 255, 0), 2)
            cv2.putText(debug_img, name, (sx, sy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Show the "Microscope" window
        cv2.imshow("Calibration View (AI Vision)", cv2.resize(debug_img, (1280, 720)))
        cv2.waitKey(1)

        # Verbose Performance Check every 5 seconds
        if time.time() - self.last_log_time > 5:
            logger.info(f"Scanning Game Window ({w}x{h}). Scaling: {scale_x:.2f}x")
            self.last_log_time = time.time()

        # Execute OCR Detection
        product_data = self._detect_product_screen(screenshot, scaled_rois)
        
        if product_data:
            product_key = f"{product_data.name}_{product_data.local_price}"
            if self._should_capture(product_key, product_data):
                self._capture_product(product_data, screenshot)

    def _detect_product_screen(self, screenshot: np.ndarray, scaled_rois: dict) -> Optional[ProductData]:
        """OCR detection using scaled coordinates"""
        try:
            # Run OCR on the specific scaled regions
            ocr_results = self.ocr_engine.extract_prices(screenshot, scaled_rois)
            
            # Process into structured data
            product_data = self.data_extractor.process_ocr_results(ocr_results)
            
            if product_data and self.data_extractor.is_valid_reading(product_data):
                return product_data
        except Exception:
            pass 
        return None

    def _should_capture(self, product_key: str, product_data: ProductData) -> bool:
        """Avoid spamming the database with the same frame"""
        current_time = time.time()
        if product_key in self.last_prices:
            last_time, last_price = self.last_prices[product_key]
            if current_time - last_time < 2.0:
                return False
        return True

    def _capture_product(self, product_data: ProductData, screenshot: np.ndarray):
        """Save data and update UI signals"""
        product_key = f"{product_data.name}_{product_data.local_price}"
        self.last_prices[product_key] = (time.time(), product_data.local_price)
        
        # Save to DB
        reading = self.db_manager.save_price_reading(
            product_name=product_data.name,
            region=product_data.region,
            local_price=product_data.local_price,
            session_id=self.session_id,
            # Add other fields as per your DB model...
        )
        
        self.capture_count_value += 1
        self.capture_count.emit(self.capture_count_value)
        self.status_update.emit(f"Captured: {product_data.name}")
        self.product_captured.emit(
            product_data.name, product_data.region, product_data.local_price, 
            0, product_data.quantity_owned, product_data.average_cost or 0, screenshot
        )

    def stop(self):
        self.running = False
        cv2.destroyAllWindows()
        self.wait(2000)

    def _cleanup(self):
        if self.session_id:
            self.db_manager.end_session(self.session_id)
        if self.screen_capture:
            self.screen_capture.close()
        cv2.destroyAllWindows()