"""
Capture Worker - Fully automated screen capture and OCR
No calibration needed - works out of the box at 2560x1440
"""

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, QMutex, QWaitCondition
from typing import Dict, Optional, List
import time
from collections import deque

from src.core.screen_capture import ScreenCapture
from src.core.ocr_engine import OCREngine
from src.core.data_extractor import DataExtractor, ProductData
from src.database.manager import DatabaseManager
from src.utils.constants import CAPTURE_SETTINGS, DEFAULT_ROIS, AUTO_DETECT

class CaptureWorker(QThread):
    """
    Automated capture worker that detects game screens and extracts prices
    No user calibration required - uses predefined coordinates for 2560x1440
    """
    
    # Signals
    product_captured = pyqtSignal(str, str, int, int, int, int, object)  # name, region, local, friend, owned, avg_cost
    status_update = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    capture_count = pyqtSignal(int) # Total products captured this session
    screenshot_captured = pyqtSignal(object, str)  # New signal: image, status
    
    
    def __init__(self, db_manager: DatabaseManager, monitor_idx: int = None):
        super().__init__()
        self.db_manager = db_manager
        self.monitor_idx = monitor_idx  # Store monitor selection
        self.running = False
        self.session_id = None
        
        # Initialize components
        self.screen_capture = None
        self.ocr_engine = OCREngine(use_gpu=True)
        self.data_extractor = DataExtractor()
        
        # State tracking
        self.current_product = None
        self.last_prices = {}  # Track last seen prices to detect changes
        self.stable_frame_count = 0
        self.frame_buffer = deque(maxlen=AUTO_DETECT['stability_frames'])
        
        # Mutex for thread safety
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        
        # Performance tracking
        self.capture_count_value = 0
        self.last_capture_time = 0
    
    def run(self):
        """Main capture loop - fully automated"""
        self.running = True
        self.status_update.emit("Initializing capture system...")
        
        try:
            # Initialize screen capture (auto-detect monitor)
            self.screen_capture = ScreenCapture()
            
            # Verify resolution with tolerance
            width, height = self.screen_capture.get_screen_resolution()
            target_w, target_h = CAPTURE_SETTINGS['resolution']
            
            # Allow 10% tolerance for resolution matching
            width_tolerance = abs(width - target_w) / target_w
            height_tolerance = abs(height - target_h) / target_h
            
            if width_tolerance > 0.1 or height_tolerance > 0.1:
                self.error_occurred.emit(
                    f"Screen resolution is {width}x{height}. "
                    f"Expected {target_w}x{target_h} (±10%). "
                    f"Please set your game to 2560x1440 on the correct monitor."
                )
                return
            
            # Start database session
            self.session_id = self.db_manager.start_session()
            self.status_update.emit("[OK] Ready - Click through your goods in-game")
            
            # Main capture loop
            while self.running:
                # Capture screen
                screenshot = self.screen_capture.capture_full_screen()
                
                # Detect which screen we're on and process accordingly
                self._process_frame(screenshot)
                
                # Cap at configured FPS
                time.sleep(1 / CAPTURE_SETTINGS['fps'])
                
        except Exception as e:
            self.error_occurred.emit(f"Capture error: {str(e)}")
        finally:
            self._cleanup()
    
    def _process_frame(self, screenshot: np.ndarray):
        """Process a single frame to detect and extract data"""
        # Try to detect product screen
        product_data = self._detect_product_screen(screenshot)
        
        if product_data:
            # Check if this is a new or updated product
            product_key = f"{product_data.name}_{product_data.local_price}"
            
            if self._should_capture(product_key, product_data):
                self._capture_product(product_data, screenshot)
        
        # Try to detect friend's price screen
        friend_data = self._detect_friend_screen(screenshot)
        
        if friend_data and self.current_product:
            # Update current product with friend price
            self._update_with_friend_price(friend_data)
    
    def _detect_product_screen(self, screenshot: np.ndarray) -> Optional[ProductData]:
        """Detect if we're on the product purchase screen and extract data"""
        try:
            # Extract regions using predefined coordinates
            rois = {
                'product_name': DEFAULT_ROIS['product_name'],
                'local_price': DEFAULT_ROIS['local_price'],
                'average_cost': DEFAULT_ROIS['average_cost'],
                'quantity_owned': DEFAULT_ROIS['quantity_owned'],
            }
            
            # Run OCR on each region
            ocr_results = self.ocr_engine.extract_prices(screenshot, rois)
            
            # Add region detection
            region_roi = DEFAULT_ROIS['region_indicator']
            region_img = screenshot[region_roi['y']:region_roi['y']+region_roi['h'], 
                                   region_roi['x']:region_roi['x']+region_roi['w']]
            region_text = self.ocr_engine.extract_text(region_img)
            ocr_results['region_text'] = region_text
            
            # Process into structured data
            product_data = self.data_extractor.process_ocr_results(ocr_results)
            
            if product_data and self.data_extractor.is_valid_reading(product_data):
                return product_data
                
        except Exception as e:
            pass  # Silent fail - screen might not be showing product
        
        return None
    
    def _detect_friend_screen(self, screenshot: np.ndarray) -> Optional[Dict]:
        """Detect if we're on the friend's price screen and extract data"""
        try:
            rois = {
                'friend_price': DEFAULT_ROIS['friend_price'],
                'vs_local': DEFAULT_ROIS['vs_local'],
                'vs_owned': DEFAULT_ROIS['vs_owned'],
            }
            
            ocr_results = self.ocr_engine.extract_prices(screenshot, rois)
            
            # Check if we got valid friend price
            if ocr_results.get('friend_price'):
                return {
                    'friend_price': ocr_results['friend_price'],
                    'vs_local': ocr_results.get('vs_local'),
                    'vs_owned': ocr_results.get('vs_owned'),
                }
                
        except Exception as e:
            pass
        
        return None
    
    def _should_capture(self, product_key: str, product_data: ProductData) -> bool:
        """Determine if we should capture this product (avoid duplicates)"""
        current_time = time.time()
        
        # Check if we recently captured this exact product/price combo
        if product_key in self.last_prices:
            last_time, last_price = self.last_prices[product_key]
            
            # Don't recapture if less than 2 seconds passed
            if current_time - last_time < 2.0:
                return False
            
            # Don't recapture if price hasn't changed significantly
            if abs(product_data.local_price - last_price) < AUTO_DETECT['price_change_threshold']:
                return False
        
        return True
    
    def _capture_product(self, product_data: ProductData, screenshot: np.ndarray = None):
        """Capture and save product data"""
        self.current_product = product_data
        
        # Update tracking
        product_key = f"{product_data.name}_{product_data.local_price}"
        self.last_prices[product_key] = (time.time(), product_data.local_price)
        
        # Save to database (without friend price yet)
        reading = self.db_manager.save_price_reading(
            product_name=product_data.name,
            region=product_data.region,
            local_price=product_data.local_price,
            friend_price=None,
            average_cost=product_data.average_cost,
            quantity_owned=product_data.quantity_owned,
            vs_local_percent=product_data.vs_local_percent,
            vs_owned_percent=product_data.vs_owned_percent,
            session_id=self.session_id
        )
        
        # Store reading ID for later friend price update
        self.current_product.reading_id = reading.id
        
        # Update UI
        self.capture_count_value += 1
        self.capture_count.emit(self.capture_count_value)
        self.status_update.emit(f"[OK] Captured: {product_data.name} @ {product_data.local_price:,}")
        
        # Emit screenshot signal
        if screenshot is not None:
            self.screenshot_captured.emit(screenshot, f"Detected: {product_data.name}")
        
        # Emit signal for UI update (with screenshot)
        self.product_captured.emit(
            product_data.name,
            product_data.region,
            product_data.local_price,
            0,
            product_data.quantity_owned,
            product_data.average_cost or 0,
            screenshot
        )
    
    def _update_with_friend_price(self, friend_data: Dict):
        """Update current product with friend price data"""
        if not self.current_product or not hasattr(self.current_product, 'reading_id'):
            return
        
        try:
            # Get the reading from database
            from src.database.models import PriceReading
            reading = self.db_manager.session.query(PriceReading).get(self.current_product.reading_id)
            
            if reading:
                # Update with friend price
                reading.friend_price = friend_data['friend_price']
                reading.vs_local_percent = friend_data.get('vs_local')
                reading.vs_owned_percent = friend_data.get('vs_owned')
                
                if reading.friend_price and reading.local_price:
                    reading.absolute_difference = reading.friend_price - reading.local_price
                
                self.db_manager.session.commit()
                
                # Update UI
                self.status_update.emit(
                    f"✓ Updated: {self.current_product.name} - "
                    f"Friend price: {friend_data['friend_price']:,}"
                )
                
                # Re-emit with complete data
                self.product_captured.emit(
                    self.current_product.name,
                    self.current_product.region,
                    self.current_product.local_price,
                    friend_data['friend_price'],
                    self.current_product.quantity_owned,
                    self.current_product.average_cost or 0
                )
                
        except Exception as e:
            print(f"Error updating friend price: {e}")
    
    def _cleanup(self):
        """Clean up resources"""
        if self.session_id:
            self.db_manager.end_session(
                self.session_id, 
                'completed' if not self.running else 'error'
            )
        
        if self.screen_capture:
            self.screen_capture.close()
        
        self.status_update.emit("Capture session ended")
    
    def stop(self):
        """Stop the capture loop gracefully"""
        self.running = False
        self.wait(3000)  # Wait up to 3 seconds for thread to finish