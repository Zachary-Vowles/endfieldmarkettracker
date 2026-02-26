"""
Screenshot log widget for visual capture history
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QFrame, QGraphicsDropShadowEffect,
                             QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap, QImage, QColor
import numpy as np
from datetime import datetime
from src.utils.constants import COLORS

class ScreenshotThumbnail(QFrame):
    clicked = pyqtSignal(str)
    
    def __init__(self, pixmap: QPixmap, timestamp: str, label: str = "", parent=None):
        super().__init__(parent)
        self.full_pixmap = pixmap
        self.timestamp = timestamp
        self.label_text = label
        self.setFixedSize(140, 100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setup_ui()
        
        self.hover_timer = QTimer()
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self.show_enlarged)
        self.enlarged_view = None
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(128, 72)
        self.image_label.setScaledContents(True)
        
        scaled = self.full_pixmap.scaled(128, 72, Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        self.image_label.setPixmap(scaled)
        layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.time_label = QLabel(self.timestamp)
        self.time_label.setStyleSheet("color: #a0a0a0; font-size: 10px; font-weight: 500;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_label)
        
        self.setStyleSheet(f"ScreenshotThumbnail {{ background-color: {COLORS['bg_dark_log']}; border: 1px solid {COLORS['border_dark']}; border-radius: 8px; }} ScreenshotThumbnail:hover {{ border: 2px solid {COLORS['accent_teal']}; }}")

    def enterEvent(self, event):
        self.hover_timer.start(400)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.hover_timer.stop()
        self.hide_enlarged()
        super().leaveEvent(event)
        
    def show_enlarged(self):
        if self.enlarged_view is None:
            self.enlarged_view = EnlargedScreenshotView(self.full_pixmap, self)
        pos = self.mapToGlobal(self.rect().topLeft())
        # Move MUCH further left to ensure mouse doesn't overlap
        self.enlarged_view.move(pos.x() - 450, pos.y() - 50)
        self.enlarged_view.show()
        self.enlarged_view.raise_()
        
    def hide_enlarged(self):
        if self.enlarged_view:
            self.enlarged_view.hide()
            
    def mousePressEvent(self, event):
        self.clicked.emit(self.timestamp)
        super().mousePressEvent(event)

class EnlargedScreenshotView(QFrame):
    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent, Qt.WindowType.ToolTip)  # Changed from Popup to ToolTip
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setup_ui(pixmap)
        
    def setup_ui(self, pixmap: QPixmap):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        scaled = pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        label = QLabel()
        label.setPixmap(scaled)
        label.setStyleSheet(f"background-color: {COLORS['bg_app']}; border: 2px solid {COLORS['accent_teal']}; border-radius: 8px; padding: 4px;")
        layout.addWidget(label)
        self.setFixedSize(scaled.width() + 24, scaled.height() + 24)

class ScreenshotLogWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setup_ui()
        self.screenshots = []
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        header = QLabel("System Log")
        header.setStyleSheet(f"color: {COLORS['text_inverse']}; font-size: 16px; font-weight: 700; padding-bottom: 8px;")
        layout.addWidget(header)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        self.thumbnails_container = QWidget()
        self.thumbnails_layout = QVBoxLayout(self.thumbnails_container)
        self.thumbnails_layout.setSpacing(12)
        self.thumbnails_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.thumbnails_container)
        layout.addWidget(scroll)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 500;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.setStyleSheet("background-color: transparent;")
    
    def add_screenshot(self, image: np.ndarray, status: str = "Captured"):
        if len(image.shape) == 3:
            h, w, c = image.shape
            q_image = QImage(image.data, w, h, c * w, QImage.Format.Format_RGB888).rgbSwapped()
        else:
            h, w = image.shape
            q_image = QImage(image.data, w, h, w, QImage.Format.Format_Grayscale8)
        
        pixmap = QPixmap.fromImage(q_image)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        thumbnail = ScreenshotThumbnail(pixmap, timestamp, status)
        self.thumbnails_layout.insertWidget(0, thumbnail)
        self.screenshots.append((timestamp, pixmap, status))
        
        if self.thumbnails_layout.count() > 20:
            item = self.thumbnails_layout.takeAt(self.thumbnails_layout.count() - 1)
            if item.widget(): item.widget().deleteLater()
                
        self.status_label.setText(f"Last update: {timestamp}")
    
    def clear_log(self):
        while self.thumbnails_layout.count():
            item = self.thumbnails_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.screenshots.clear()
        self.status_label.setText("Ready")
        
    def update_status(self, message: str):
        self.status_label.setText(message)