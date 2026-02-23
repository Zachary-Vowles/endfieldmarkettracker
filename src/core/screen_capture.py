"""
Screen capture functionality
Uses MSS for high-performance screen capture
"""

import cv2
import numpy as np
import mss
import mss.tools
from typing import Dict, Optional, Tuple
from PyQt6.QtCore import QThread, pyqtSignal

class ScreenCapture:
    """Handles screen capture operations"""
    
    def __init__(self, monitor_idx: int = 0):
        """Initialize screen capture"""
        self.sct = mss.mss()
        self.monitor_idx = monitor_idx
        self.monitors = self.sct.monitors
        
        # Default to primary monitor if index invalid
        if monitor_idx >= len(self.monitors):
            self.monitor_idx = 0
    
    def capture_full_screen(self) -> np.ndarray:
        """Capture the entire screen"""
        monitor = self.monitors[self.monitor_idx]
        screenshot = self.sct.grab(monitor)
        
        # Convert to numpy array (BGR format for OpenCV)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        return img
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """Capture a specific region"""
        monitor = {
            "left": x,
            "top": y,
            "width": width,
            "height": height
        }
        
        screenshot = self.sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        return img
    
    def get_screen_resolution(self) -> Tuple[int, int]:
        """Get the current screen resolution"""
        monitor = self.monitors[self.monitor_idx]
        return monitor["width"], monitor["height"]
    
    def close(self):
        """Clean up resources"""
        self.sct.close()


class CaptureThread(QThread):
    """Thread for continuous screen capture"""
    
    frame_captured = pyqtSignal(np.ndarray)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, monitor_idx: int = 0, fps: int = 10):
        super().__init__()
        self.monitor_idx = monitor_idx
        self.fps = fps
        self.running = False
        self.capture = None
    
    def run(self):
        """Main capture loop"""
        self.running = True
        self.capture = ScreenCapture(self.monitor_idx)
        
        try:
            while self.running:
                frame = self.capture.capture_full_screen()
                self.frame_captured.emit(frame)
                
                # Cap at specified FPS
                self.msleep(int(1000 / self.fps))
                
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            if self.capture:
                self.capture.close()
    
    def stop(self):
        """Stop the capture loop"""
        self.running = False
        self.wait(2000)