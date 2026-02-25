import mss
import numpy as np
import pygetwindow as gw
import psutil  # Added to check the process name
import cv2
from loguru import logger

class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()
        self.window_title = "Endfield" 
        self.process_name = "Endfield.exe"  # The exact process name

    def get_game_window_rect(self):
        """Locates the game window boundaries by title or process name."""
        try:
            # Search for windows with the exact title
            windows = [w for w in gw.getAllWindows() if w.title == self.window_title]

            # Check if we found the window
            if windows:
                win = windows[0]
                if win.isMinimized:
                    return None

                # Check if the window belongs to the correct process
                process_id = win._pid
                process = psutil.Process(process_id)
                if process.name() == self.process_name:
                    # Return the window's dimensions if it matches the process
                    return {"top": win.top, "left": win.left, "width": win.width, "height": win.height}
                else:
                    logger.warning(f"Found window with title '{self.window_title}', but the process name doesn't match '{self.process_name}'.")
            else:
                logger.warning(f"No window with title '{self.window_title}' found.")

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