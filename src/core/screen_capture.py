import mss
import numpy as np
import pygetwindow as gw
import cv2
from loguru import logger

class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()
        self.window_title = "Endfield" 

    def get_game_window_rect(self):
        """Locates the game window boundaries."""
        try:
            windows = gw.getWindowsWithTitle(self.window_title)
            if windows:
                win = windows[0]
                if win.isMinimized: return None
                return {"top": win.top, "left": win.left, "width": win.width, "height": win.height}
        except Exception as e:
            logger.error(f"Window search failed: {e}")
        return None

    def capture_full_screen(self):
        """Captures only the game window area."""
        rect = self.get_game_window_rect()
        if rect:
            monitor = {"top": rect["top"], "left": rect["left"], "width": rect["width"], "height": rect["height"]}
        else:
            monitor = self.sct.monitors[1]
            
        screenshot = self.sct.grab(monitor)
        img = np.array(screenshot)
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