
import cv2
import numpy as np
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QMessageBox, QProgressBar, QFrame) 
from PyQt6.QtCore import Qt, QTimer
from src.utils.constants import DEFAULT_ROIS
from src.core.screen_capture import ScreenCapture
import time

class CalibrationWizard(QDialog):
    """Simple wizard to calibrate OCR detection regions for Endfield"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calibration Wizard - Capture Endfield Price Boxes")
        self.setMinimumSize(450, 400)
        
        self.rois = {}  # Store new coordinates
        self.current_step = 0
        self.calibration_steps = [
            ("product_name", "Product Name", "Click and drag around the product name text (e.g., 'Wuling Frozen Pears')"),
            ("local_price", "Local Price", "Draw a box around the LOCAL price (the big HZ number on the right side)"),
            ("friend_price", "Friend Price", "Draw a box around the FRIEND price area"),
            ("average_cost", "Average Cost", "Draw a box around your average cost (if visible, or skip)"),
            ("quantity_owned", "Quantity", "Draw a box around quantity owned number"),
        ]
        
        self.capture = ScreenCapture()
        self.setup_ui()
        
        # Check if game is running
        self.verify_game_window()
        
    def verify_game_window(self):
        """Make sure Endfield is actually running"""
        test_capture = self.capture.capture_full_screen()
        if test_capture is None:
            QMessageBox.critical(
                self, 
                "Game Not Found", 
                "Could not find Endfield window!\n\n"
                "Please make sure the game is running before calibrating.\n"
                "The game should be visible on your screen."
            )
            self.reject()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("Calibration Setup")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00d4aa;")
        layout.addWidget(title)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMaximum(len(self.calibration_steps))
        self.progress.setValue(0)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #00d4aa;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress)
        
        # Current step label
        self.step_label = QLabel(f"Step 1 of {len(self.calibration_steps)}")
        self.step_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        layout.addWidget(self.step_label)
        
        # Instruction box
        self.instruction_box = QFrame()
        self.instruction_box.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        instruction_layout = QVBoxLayout(self.instruction_box)
        
        self.current_item = QLabel(self.calibration_steps[0][1])
        self.current_item.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        instruction_layout.addWidget(self.current_item)
        
        self.instruction = QLabel(self.calibration_steps[0][2])
        self.instruction.setStyleSheet("font-size: 13px; color: #a0a0a0; padding-top: 8px;")
        self.instruction.setWordWrap(True)
        instruction_layout.addWidget(self.instruction)
        
        layout.addWidget(self.instruction_box)
        
        # Status label
        self.status = QLabel("Click 'Capture Screenshot' to grab the game screen")
        self.status.setStyleSheet("color: #ffd700; font-size: 12px; padding: 8px;")
        layout.addWidget(self.status)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.capture_btn = QPushButton("📷 Capture Screenshot")
        self.capture_btn.setStyleSheet("""
            QPushButton {
                background-color: #00d4aa;
                color: #0d0d0d;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #00a884;
            }
            QPushButton:disabled {
                background-color: #3a3a3a;
                color: #666;
            }
        """)
        self.capture_btn.clicked.connect(self.capture_screenshot)
        btn_layout.addWidget(self.capture_btn)
        
        self.skip_btn = QPushButton("Skip This")
        self.skip_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #a0a0a0;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        self.skip_btn.clicked.connect(self.skip_current)
        btn_layout.addWidget(self.skip_btn)
        
        layout.addLayout(btn_layout)
        
        # Save button (enabled at end)
        self.save_btn = QPushButton("💾 Save Calibration")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
            QPushButton:disabled {
                background-color: #3a3a3a;
                color: #666;
            }
        """)
        self.save_btn.clicked.connect(self.save_calibration)
        self.save_btn.setEnabled(False)
        layout.addWidget(self.save_btn)
        
        # Summary label
        self.summary = QLabel("")
        self.summary.setStyleSheet("color: #4caf50; font-size: 11px;")
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        
        layout.addStretch()
        
        # Help text
        help_text = QLabel("Tip: Make sure Endfield is visible behind this window. The capture will grab the game directly, not your desktop.")
        help_text.setStyleSheet("color: #666; font-size: 10px; font-style: italic;")
        help_text.setWordWrap(True)
        layout.addWidget(help_text)
        
    def capture_screenshot(self):
        """Grab screenshot from Endfield window specifically"""
        self.status.setText("Capturing... make sure game is visible")
        self.status.repaint()
        
        # Small delay so user can see the message
        QTimer.singleShot(500, self._do_capture)
        
    def _do_capture(self):
        """Actual capture - specifically targets Endfield window"""
        self.status.setText("Capturing Endfield window...")
        self.status.repaint()
        
        # Minimize ourselves so we don't get in the way
        self.showMinimized()
        
        # Give time for minimize animation and user to see game
        QTimer.singleShot(800, self._capture_game_window)
        
    def _capture_game_window(self):
        """Capture after we've minimized"""
        screenshot = self.capture.capture_full_screen()
        
        # Restore our window
        self.showNormal()
        self.raise_()
        self.activateWindow()
        
        if screenshot is None:
            QMessageBox.critical(self, "Capture Failed", 
                "Could not capture Endfield window.\n\n"
                "Make sure the game is running and not minimized.")
            return
            
        # Store original for coordinate mapping
        self.last_screenshot = screenshot
        h, w = screenshot.shape[:2]
        
        # Resize for display if too large (OpenCV windows have max size around 1920x1080)
        display_scale = 1.0
        if w > 1600 or h > 900:
            display_scale = min(1600 / w, 900 / h)
            display_img = cv2.resize(screenshot, None, fx=display_scale, fy=display_scale)
        else:
            display_img = screenshot
            
        step_key, step_name, step_desc = self.calibration_steps[self.current_step]
        
        # Create window with instructions in title
        window_title = f"Draw box for: {step_name} | ENTER=confirm, C=cancel"
        
        # Position OpenCV window away from our app
        cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
        cv2.moveWindow(window_title, 100, 100)
        cv2.resizeWindow(window_title, int(w * display_scale), int(h * display_scale))
        
        # OpenCV ROI selector
        roi = cv2.selectROI(window_title, display_img, fromCenter=False, showCrosshair=True)
        cv2.destroyAllWindows()
        
        # Check if user cancelled (roi will be all zeros)
        if roi[2] == 0 or roi[3] == 0:
            self.status.setText("Selection cancelled. Try again.")
            return
            
        # Scale back up if we resized for display
        if display_scale < 1.0:
            roi = (
                int(roi[0] / display_scale),
                int(roi[1] / display_scale),
                int(roi[2] / display_scale),
                int(roi[3] / display_scale)
            )
        
        # Store the ROI
        self.rois[step_key] = {
            'x': roi[0], 
            'y': roi[1], 
            'w': roi[2], 
            'h': roi[3]
        }
        
        # Update UI
        self.status.setText(f"✓ Captured {step_name}: ({roi[0]}, {roi[1]}) size {roi[2]}x{roi[3]}")
        self.update_summary()
        
        # Auto-advance to next step
        self.next_step()    
            
    def skip_current(self):
        """Skip current calibration step"""
        self.current_step += 1
        self.progress.setValue(self.current_step)
        
        if self.current_step < len(self.calibration_steps):
            next_key, next_name, next_desc = self.calibration_steps[self.current_step]
            self.step_label.setText(f"Step {self.current_step + 1} of {len(self.calibration_steps)}")
            self.current_item.setText(next_name)
            self.instruction.setText(next_desc)
            self.status.setText(f"Skipped. Now: {next_name}")
        else:
            self.step_label.setText("Complete!")
            self.capture_btn.setEnabled(False)
            self.skip_btn.setEnabled(False)
            if len(self.rois) > 0:
                self.save_btn.setEnabled(True)
                
    def update_summary(self):
        """Show what we've captured so far"""
        lines = ["Captured regions:"]
        for key, roi in self.rois.items():
            # Find display name
            name = key.replace("_", " ").title()
            lines.append(f"  • {name}: ({roi['x']}, {roi['y']}) {roi['w']}x{roi['h']}")
        self.summary.setText("\n".join(lines))
        
    def save_calibration(self):
        """Save to config file and update constants"""
        if not self.rois:
            QMessageBox.warning(self, "Nothing to save", "No regions were captured.")
            return
            
        try:
            from src.utils.config import get_config, save_config
            config = get_config()
            
            # Merge with existing ROIs (update only what we captured)
            for key, value in self.rois.items():
                config.rois[key] = value
                
            save_config()
            
            # Also update the in-memory constants for immediate use
            import src.utils.constants as constants
            for key, value in self.rois.items():
                constants.DEFAULT_ROIS[key] = value
            
            count = len(self.rois)
            QMessageBox.information(
                self, 
                "Calibration Saved!", 
                f"Successfully saved {count} region(s).\n\n"
                f"The app will now use your custom calibration.\n"
                f"Restart the capture to use new settings."
            )
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Could not save calibration: {str(e)}")