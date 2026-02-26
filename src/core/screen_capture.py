import mss
import numpy as np
import pygetwindow as gw
import psutil
import cv2
import win32gui
import win32process
from loguru import logger
import ctypes
from ctypes import wintypes
import os


def capture_full_screen(self):
    """Captures only the game window area."""
    rect = self.get_game_window_rect()
    
    if rect:
        monitor = {
            "top": rect["top"],
            "left": rect["left"],
            "width": rect["width"],
            "height": rect["height"]
        }
        
        # DEBUG: Log what we're about to capture
        logger.info(f"Attempting capture at: {monitor}")
        
        # Verify this isn't the full desktop
        full_screen = self.sct.monitors[0]  # All monitors combined
        if monitor["width"] >= full_screen["width"] and monitor["height"] >= full_screen["height"]:
            logger.warning("Capture region is full screen size! Window might be fullscreen/borderless.")
            
    else:
        logger.warning("No window rect, falling back to full screen")
        monitor = self.sct.monitors[1]

        screenshot = self.sct.grab(monitor)
        img = np.array(screenshot)
    
        # DEBUG: Save what was actually captured
        debug_path = "last_capture_debug.png"
        cv2.imwrite(debug_path, cv2.cvtColor(img, cv2.COLOR_BGRA2BGR))
        logger.info(f"Saved debug screenshot to {debug_path}, shape: {img.shape}")
    
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()
        self.window_title = "Endfield"
        self.process_name = "Endfield.exe"
        self.cached_rect = None

    def get_window_pid(self, hwnd):
        """Get process ID from window handle using Win32 API."""
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return pid
        except Exception:
            return None

    def get_client_rect(self, hwnd):
        """
        Get the client area (actual game render area) excluding title bar and borders.
        Returns dict with top, left, width, height.
        """
        try:
            # Get client rectangle (relative to window, not screen)
            left, top, right, bottom = win32gui.GetClientRect(hwnd)
            
            # Convert client coordinates to screen coordinates
            client_left, client_top = win32gui.ClientToScreen(hwnd, (left, top))
            client_right, client_bottom = win32gui.ClientToScreen(hwnd, (right, bottom))
            
            return {
                "top": client_top,
                "left": client_left,
                "width": client_right - client_left,
                "height": client_bottom - client_top
            }
        except Exception as e:
            logger.error(f"Failed to get client rect: {e}")
            return None

    def get_game_window_rect(self):
        """Locates the game window boundaries by title or process name."""
        try:
            windows = [w for w in gw.getAllWindows() if w.title == self.window_title]

            if not windows:
                # logger.warning(f"No window with title '{self.window_title}' found.")
                return None

            win = windows[0]
        
            if win.isMinimized:
                # logger.warning(f"Window '{self.window_title}' is minimized.")
                return None

            hwnd = win._hWnd
            process_id = self.get_window_pid(hwnd)
        
            if process_id is None:
                return None

            try:
                process = psutil.Process(process_id)
                actual_process_name = process.name()
            
                if actual_process_name.lower() != self.process_name.lower():
                    # logger.warning(
                    #     f"Found window with title '{self.window_title}', "
                    #     f"but process name is '{actual_process_name}', not '{self.process_name}'."
                    # )
                    return None

                # Use client rect instead of window rect to exclude borders
                rect = self.get_client_rect(hwnd)
                if rect:
                    # logger.info(
                    #     f"Found window: {win.title} (PID: {process_id}, "
                    #     f"Process: {actual_process_name}, Rect: {rect})"
                    # )
                    self.cached_rect = rect
                    return rect
                
            except psutil.NoSuchProcess:
                # logger.warning(f"Process {process_id} no longer exists.")
                return None

        except Exception as e:
            # logger.error(f"Window search failed: {e}")
            pass
        
        # Return cached rect if available and window exists but had an error
        if self.cached_rect:
            # logger.debug("Using cached window rectangle")
            return self.cached_rect
        return None

    def capture_full_screen(self):
        """Captures only the game window area."""
        rect = self.get_game_window_rect()
        
        if rect:
            # Ensure coordinates are positive and reasonable    
            if rect["width"] <= 0 or rect["height"] <= 0:
                logger.error(f"Invalid window dimensions: {rect}")
                rect = None
                
        if rect:
            monitor = {
                "top": rect["top"],
                "left": rect["left"],
                "width": rect["width"],
                "height": rect["height"]
            }
            logger.debug(f"Capturing region: {monitor}")
        else:
            logger.warning("Falling back to full screen capture.")
            monitor = self.sct.monitors[1]

        screenshot = self.sct.grab(monitor)
        img = np.array(screenshot)
        
        #not sure if this debug screencapture works - yes it does, but only captures the very last thing seen, which is the window itself
        debug_path = "last_capture_debug.png"
        cv2.imwrite(debug_path, cv2.cvtColor(img, cv2.COLOR_BGRA2BGR))
        logger.info(f"Saved debug screenshot to: {os.path.abspath(debug_path)}")
        
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    def get_screen_resolution(self):
        """Returns current window width and height for scaling math."""
        rect = self.get_game_window_rect()
        if rect:
            return rect["width"], rect["height"]
        monitor = self.sct.monitors[1]
        return monitor["width"], monitor["height"]

    def close(self):
        """Clean shutdown to prevent AttributeErrors."""
        self.sct.close()