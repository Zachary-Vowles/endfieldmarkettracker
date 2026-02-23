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

class ScreenshotThumbnail(QFrame):
    """Individual screenshot thumbnail with hover enlarge effect"""
    
    clicked = pyqtSignal(str)  # Emit screenshot path on click
    
    def __init__(self, pixmap: QPixmap, timestamp: str, label: str = "", parent=None):
        super().__init__(parent)
        self.full_pixmap = pixmap
        self.timestamp = timestamp
        self.label_text = label
        self.setFixedSize(120, 90)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setup_ui()
        
        # Hover timer for enlarge effect
        self.hover_timer = QTimer()
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self.show_enlarged)
        self.enlarged_view = None
        
    def setup_ui(self):
        """Setup the thumbnail UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        # Thumbnail image
        self.image_label = QLabel()
        self.image_label.setFixedSize(112, 63)
        self.image_label.setScaledContents(True)
        
        # Scale pixmap to fit
        scaled = self.full_pixmap.scaled(112, 63, Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        self.image_label.setPixmap(scaled)
        
        layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Timestamp label
        self.time_label = QLabel(self.timestamp)
        self.time_label.setStyleSheet("color: #888; font-size: 9px;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_label)
        
        # Status label (e.g., "Detected", "Processing")
        if self.label_text:
            self.status_label = QLabel(self.label_text)
            self.status_label.setStyleSheet("color: #4caf50; font-size: 8px; font-weight: bold;")
            self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.status_label)
        
        # Styling
        self.setStyleSheet("""
            ScreenshotThumbnail {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
            }
            ScreenshotThumbnail:hover {
                border: 2px solid #00d4aa;
                background-color: #333;
            }
        """)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
    
    def enterEvent(self, event):
        """Mouse entered - start hover timer"""
        self.hover_timer.start(300)  # 300ms delay
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Mouse left - cancel timer and hide enlarged view"""
        self.hover_timer.stop()
        self.hide_enlarged()
        super().leaveEvent(event)
    
    def show_enlarged(self):
        """Show enlarged screenshot view"""
        if self.enlarged_view is None:
            self.enlarged_view = EnlargedScreenshotView(self.full_pixmap, self)
        
        # Position near the thumbnail but ensure it stays on screen
        pos = self.mapToGlobal(self.rect().topLeft())
        self.enlarged_view.move(pos.x() - 50, pos.y() - 250)
        self.enlarged_view.show()
        self.enlarged_view.raise_()
    
    def hide_enlarged(self):
        """Hide enlarged view"""
        if self.enlarged_view:
            self.enlarged_view.hide()
    
    def mousePressEvent(self, event):
        """Handle click"""
        self.clicked.emit(self.timestamp)
        super().mousePressEvent(event)


class EnlargedScreenshotView(QFrame):
    """Enlarged screenshot popup on hover"""
    
    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setup_ui(pixmap)
    
    def setup_ui(self, pixmap: QPixmap):
        """Setup the enlarged view"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Scale to reasonable size (max 400x300)
        scaled = pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio, 
                               Qt.TransformationMode.SmoothTransformation)
        
        label = QLabel()
        label.setPixmap(scaled)
        label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 2px solid #00d4aa;
                border-radius: 8px;
                padding: 4px;
            }
        """)
        
        layout.addWidget(label)
        self.setFixedSize(scaled.width() + 24, scaled.height() + 24)
        
        # Styling
        self.setStyleSheet("""
            EnlargedScreenshotView {
                background-color: transparent;
            }
        """)


class ScreenshotLogWidget(QFrame):
    """Widget showing screenshot capture history"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(280)
        self.setup_ui()
        self.screenshots = []
        
    def setup_ui(self):
        """Setup the log widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Header
        header = QLabel("Capture Log")
        header.setStyleSheet("""
            color: #fff;
            font-size: 14px;
            font-weight: bold;
            padding-bottom: 8px;
            border-bottom: 1px solid #3a3a3a;
        """)
        layout.addWidget(header)
        
        # Scroll area for thumbnails
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1a1a1a;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #3a3a3a;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #555;
            }
        """)
        
        # Container for thumbnails
        self.thumbnails_container = QWidget()
        self.thumbnails_layout = QVBoxLayout(self.thumbnails_container)
        self.thumbnails_layout.setSpacing(8)
        self.thumbnails_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.thumbnails_container)
        layout.addWidget(scroll)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #888; font-size: 11px; padding-top: 8px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Styling
        self.setStyleSheet("""
            ScreenshotLogWidget {
                background-color: #1e1e1e;
                border-left: 1px solid #3a3a3a;
            }
        """)
    
    def add_screenshot(self, image: np.ndarray, status: str = "Captured"):
        """Add a new screenshot to the log"""
        # Convert numpy array to QPixmap
        if len(image.shape) == 3:
            height, width, channels = image.shape
            bytes_per_line = channels * width
            q_image = QImage(image.data, width, height, bytes_per_line, 
                           QImage.Format.Format_RGB888).rgbSwapped()
        else:
            height, width = image.shape
            q_image = QImage(image.data, width, height, width, 
                           QImage.Format.Format_Grayscale8)
        
        pixmap = QPixmap.fromImage(q_image)
        
        # Create timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Create thumbnail
        thumbnail = ScreenshotThumbnail(pixmap, timestamp, status)
        thumbnail.clicked.connect(self.on_thumbnail_clicked)
        
        # Add to layout at top
        self.thumbnails_layout.insertWidget(0, thumbnail)
        self.screenshots.append((timestamp, pixmap, status))
        
        # Limit to last 20 screenshots
        if self.thumbnails_layout.count() > 20:
            item = self.thumbnails_layout.takeAt(self.thumbnails_layout.count() - 1)
            if item.widget():
                item.widget().deleteLater()
        
        self.status_label.setText(f"Last capture: {timestamp}")
    
    def on_thumbnail_clicked(self, timestamp: str):
        """Handle thumbnail click"""
        print(f"[INFO] Screenshot clicked: {timestamp}")
    
    def clear_log(self):
        """Clear all screenshots"""
        while self.thumbnails_layout.count():
            item = self.thumbnails_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.screenshots.clear()
        self.status_label.setText("Ready")
    
    def update_status(self, message: str):
        """Update status label"""
        self.status_label.setText(message)