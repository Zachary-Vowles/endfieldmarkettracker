"""
Capture Worker - Fully automated screen capture and OCR
No calibration needed - works out of the box at 2560x1440
"""

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, QMutex, QWaitCondition, QMutexLocker
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
        
        # Load ROIs from config (calibrated values) or use defaults
        from src.utils.config import get_config
        config = get_config()
        
        # IMPORTANT: Use config ROIs if they exist and have data, else defaults
        if config.rois and len(config.rois) > 0:
            self.rois = config.rois
            logger.info(f"Loaded {len(self.rois)} calibrated ROIs from config")
        else:
            self.rois = DEFAULT_ROIS
            logger.info("Using default ROIs (no calibration found)")
        
        # Log what we're using
        for name, roi in self.rois.items():
            logger.info(f"  ROI {name}: {roi}")
        
        # Initialize components
        self.screen_capture = ScreenCapture()
        self.ocr_engine = OCREngine(use_gpu=True)
        self.data_extractor = DataExtractor()
        
        # State tracking
        self.current_product = None
        self.last_prices = {}  
        self.last_log_time = 0
        self.capture_count_value = 0
        self.last_error_log = 0
        
        # Mutex for thread safety
        self.mutex = QMutex()
        
        # Debug window state
        self.debug_window_created = False
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
        
        # Create Debug View at reasonable size (1280x720 max)
        # Use a copy so we don't modify original for OCR
        debug_scale = min(1280 / w, 720 / h, 1.0)  # Scale down if needed, never up
        if debug_scale < 1.0:
            debug_width = int(w * debug_scale)
            debug_height = int(h * debug_scale)
            debug_img = cv2.resize(screenshot, (debug_width, debug_height))
        else:
            debug_img = screenshot.copy()
            debug_width, debug_height = w, h
        
        # Scale ROIs for the debug view display
        display_scale = debug_scale if debug_scale < 1.0 else 1.0
        for name, roi in self.rois.items():
            sx = int(roi['x'] * scale_x * display_scale)
            sy = int(roi['y'] * scale_y * display_scale)
            sw = int(roi['w'] * scale_x * display_scale)
            sh = int(roi['h'] * scale_y * display_scale)
            
            # Draw green boxes for calibration
            cv2.rectangle(debug_img, (sx, sy), (sx + sw, sy + sh), (0, 255, 0), 2)
            cv2.putText(debug_img, name, (sx, sy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Show the debug window - use fixed size to prevent recursion
        window_name = "Calibration View (AI Vision)"
        if not self.debug_window_created:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 1280, 720)  # Fixed size, not auto
            # Position away from center to avoid capturing itself
            cv2.moveWindow(window_name, 50, 50)
            self.debug_window_created = True
            
        cv2.imshow(window_name, debug_img)
        cv2.waitKey(1)

        # Verbose Performance Check every 5 seconds
        if time.time() - self.last_log_time > 5:
            logger.info(f"Scanning Game Window ({w}x{h}). Scaling: {scale_x:.2f}x, Debug: {debug_scale:.2f}x")
            self.last_log_time = time.time()

        # Execute OCR Detection (use full resolution for OCR)
        full_scaled_rois = {}
        for name, roi in self.rois.items():
            sx, sy = int(roi['x'] * scale_x), int(roi['y'] * scale_y)
            sw, sh = int(roi['w'] * scale_x), int(roi['h'] * scale_y)
            full_scaled_rois[name] = {'x': sx, 'y': sy, 'w': sw, 'h': sh}
        
        product_data = self._detect_product_screen(screenshot, full_scaled_rois)
        
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
                
        except Exception as e:
            logger.warning(f"OCR detection failed: {type(e).__name__}: {e}")
            # Only log full details every 10 seconds to avoid spam
            if time.time() - self.last_error_log > 10:
                logger.error(f"OCR debug info - Screenshot shape: {screenshot.shape if screenshot is not None else 'None'}")
                self.last_error_log = time.time()
                
        return None

    def _should_capture(self, product_key: str, product_data: ProductData) -> bool:
        """Avoid spamming the database with the same frame"""
        with QMutexLocker(self.mutex):
            current_time = time.time()
            if product_key in self.last_prices:
                last_time, last_price = self.last_prices[product_key]
                if current_time - last_time < 2.0:
                    return False
            self.last_prices[product_key] = (current_time, product_data.local_price)
            return True

    def _capture_product(self, product_data: ProductData, screenshot: np.ndarray):
        """Save data and update UI signals"""
        product_key = f"{product_data.name}_{product_data.local_price}"
        
        # Save to DB
        reading = self.db_manager.save_price_reading(
            product_name=product_data.name,
            region=product_data.region,
            local_price=product_data.local_price,
            session_id=self.session_id,
        )
        
        self.capture_count_value += 1
        self.capture_count.emit(self.capture_count_value)
        self.status_update.emit(f"Captured: {product_data.name}")
        self.product_captured.emit(
            product_data.name, product_data.region, product_data.local_price, 
            0, product_data.quantity_owned, product_data.average_cost or 0, screenshot
        )

    def stop(self):
        """Stop the capture session safely"""
        logger.info("Stop requested - signaling thread to end...")
        self.running = False
        
        # Don't wait forever - give it 2 seconds then force close
        if not self.wait(2000):  # Wait up to 2 seconds
            logger.warning("Thread did not stop gracefully, terminating...")
            self.terminate()
            self.wait(1000)  # Wait a bit more after terminate
        
        # Cleanup happens in finally block of run(), but ensure it's called
        self._cleanup()
        logger.info("Stop complete")

    def _cleanup(self):
        """Ensure all resources are released properly"""
        try:
            # Close database session first
            if self.session_id:
                self.db_manager.end_session(self.session_id)
                self.session_id = None
                
            # Close screen capture
            if self.screen_capture:
                self.screen_capture.close()
                self.screen_capture = None
                
        finally:
            # This ALWAYS runs, even if errors occurred above
            if self.debug_window_created:
                cv2.destroyWindow("Calibration View (AI Vision)")
                cv2.waitKey(1)
                self.debug_window_created = False
            
            # Clear GPU memory if available
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    logger.info("GPU memory cleared")
            except:
                pass  # If torch isn't available, ignore    