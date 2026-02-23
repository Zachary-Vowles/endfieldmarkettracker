"""
Screen capture functionality
Uses MSS for high-performance screen capture
"""

import cv2
import numpy as np
import mss
import mss.tools
from typing import Dict, Optional, Tuple, List
from PyQt6.QtCore import QThread, pyqtSignal

class ScreenCapture:
    """Handles screen capture operations"""
    
    def __init__(self, monitor_idx: int = None):
        """Initialize screen capture
        Args:
            monitor_idx: Which monitor to capture (None = auto-detect by resolution)
        """
        self.sct = mss.mss()
        self.monitors = self.sct.monitors  # List of all monitors
        self.monitor_idx = monitor_idx or self._find_target_monitor()
        
        print(f"[INFO] Available monitors:")
        for i, mon in enumerate(self.monitors[1:], 1):  # Skip index 0 (all monitors combined)
            print(f"  Monitor {i}: {mon['width']}x{mon['height']} at ({mon['left']},{mon['top']})")
        print(f"[INFO] Using monitor {self.monitor_idx}: {self.get_screen_resolution()}")
    
    def _find_target_monitor(self) -> int:
        """Find the monitor with 2560x1440 resolution"""
        target_res = (2560, 1440)
        
        # Check all monitors (skip index 0 which is all monitors combined)
        for i in range(1, len(self.monitors)):
            mon = self.monitors[i]
            if (mon['width'], mon['height']) == target_res:
                return i
        
        # If not found, check for closest match (within 10% tolerance)
        print("[WARNING] Exact 2560x1440 monitor not found, looking for closest match...")
        closest_idx = 1
        closest_diff = float('inf')
        
        for i in range(1, len(self.monitors)):
            mon = self.monitors[i]
            # Calculate resolution difference
            diff = abs(mon['width'] - target_res[0]) + abs(mon['height'] - target_res[1])
            if diff < closest_diff:
                closest_diff = diff
                closest_idx = i
        
        # If within 10% tolerance, use it
        mon = self.monitors[closest_idx]
        width_diff_pct = abs(mon['width'] - target_res[0]) / target_res[0]
        height_diff_pct = abs(mon['height'] - target_res[1]) / target_res[1]
        
        if width_diff_pct < 0.1 and height_diff_pct < 0.1:
            print(f"[WARNING] Using closest match: {mon['width']}x{mon['height']}")
            return closest_idx
        
        # Default to primary monitor if nothing matches
        print(f"[WARNING] No suitable monitor found, using monitor 1")
        return 1
    
    def capture_full_screen(self) -> np.ndarray:
        """Capture the entire selected monitor"""
        monitor = self.monitors[self.monitor_idx]
        screenshot = self.sct.grab(monitor)
        
        # Convert to numpy array (BGR format for OpenCV)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        return img
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """Capture a specific region (relative to selected monitor)"""
        monitor = self.monitors[self.monitor_idx]
        
        # Adjust coordinates relative to monitor position
        monitor_left = monitor.get('left', 0)
        monitor_top = monitor.get('top', 0)
        
        region = {
            "left": monitor_left + x,
            "top": monitor_top + y,
            "width": width,
            "height": height
        }
        
        screenshot = self.sct.grab(region)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        return img
    
    def get_screen_resolution(self) -> Tuple[int, int]:
        """Get the current screen resolution"""
        monitor = self.monitors[self.monitor_idx]
        return monitor["width"], monitor["height"]
    
    def get_all_monitors(self) -> List[Dict]:
        """Get info about all available monitors"""
        return self.monitors[1:]  # Skip the "all monitors" entry
    
    def close(self):
        """Clean up resources"""
        self.sct.close()


class CaptureThread(QThread):
    """Thread for continuous screen capture"""
    
    frame_captured = pyqtSignal(np.ndarray)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, monitor_idx: int = None, fps: int = 10):
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