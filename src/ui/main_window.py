"""
Main application window for Endfield Market Tracker
Updated with working capture and price history charts
"""

import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTabWidget, QScrollArea, 
                             QGridLayout, QFrame, QStatusBar, QMessageBox,
                             QComboBox, QSplitter)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

import pyqtgraph as pg
from pyqtgraph import PlotWidget, mkPen, mkBrush

from src.ui.styles import get_main_stylesheet
from src.ui.product_card import ProductCard
from src.database.manager import DatabaseManager
from src.core.capture_worker import CaptureWorker
from src.utils.constants import COLORS
from src.ui.screenshot_log import ScreenshotLogWidget

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Endfield Market Tracker")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # Initialize database
        self.db_manager = DatabaseManager()
        
        # Capture worker
        self.capture_worker = None
        
        # Track captured products for UI
        self.product_cards = {}
        
        # Setup UI
        self.setup_ui()
        self.apply_styles()
        
        # Load initial data
        self.load_todays_data()
        self.load_price_history()
        
        # Setup auto-refresh timer for charts
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
    
    def setup_ui(self):
        """Setup the main UI"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout (content + screenshot log)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left side container (header + tabs)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        left_layout.addWidget(header)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        
        # Today's Trades tab
        self.trades_tab = self.create_trades_tab()
        self.tab_widget.addTab(self.trades_tab, "Today's Trades")
        
        # Price History tab
        self.history_tab = self.create_history_tab()
        self.tab_widget.addTab(self.history_tab, "Price History")
        
        left_layout.addWidget(self.tab_widget, stretch=1)
        main_layout.addWidget(left_container, stretch=1)
        
        # Right side - Screenshot log
        self.screenshot_log = ScreenshotLogWidget()
        main_layout.addWidget(self.screenshot_log)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Click Start and browse your goods in-game")


    def create_header(self):
        """Create the header section with controls"""
        header = QFrame()
        header.setObjectName("header")
        header.setStyleSheet(f"""
            QFrame#header {{
                background-color: {COLORS['bg_secondary']};
                border-bottom: 1px solid {COLORS['border_light']};
            }}
        """)
        header.setFixedHeight(80)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 12, 24, 12)
        
        # Title
        title_layout = QVBoxLayout()
        title = QLabel("Endfield Market Tracker")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        title_layout.addWidget(title)
        
        subtitle = QLabel("2560x1440 Auto-Capture | No calibration needed")
        subtitle.setStyleSheet(f"color: {COLORS['accent_teal']}; font-size: 12px;")
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Capture counter
        self.capture_counter = QLabel("Captured: 0")
        self.capture_counter.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 14px;
            padding-right: 20px;
        """)
        layout.addWidget(self.capture_counter)
                
        
        # Monitor selector (for multi-monitor setups)
        monitor_label = QLabel("Monitor:")
        monitor_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(monitor_label)
        
        self.monitor_selector = QComboBox()
        self.monitor_selector.setMinimumWidth(100)
        self.monitor_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border_light']};
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        
        # Populate with available monitors
        from src.core.screen_capture import ScreenCapture
        temp_capture = ScreenCapture.__new__(ScreenCapture)
        temp_capture.sct = __import__('mss').mss()
        temp_capture.monitors = temp_capture.sct.monitors
        
        for i in range(1, len(temp_capture.monitors)):
            mon = temp_capture.monitors[i]
            self.monitor_selector.addItem(f"{i}: {mon['width']}x{mon['height']}")
        
        temp_capture.sct.close()
        layout.addWidget(self.monitor_selector)
        
        layout.addSpacing(20)  # Add some space before buttons


         # Control buttons
        self.start_btn = QPushButton("Start")
        self.start_btn.setObjectName("startButton")
        self.start_btn.setFixedWidth(120)
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)  # Set cursor in Python
        self.start_btn.clicked.connect(self.start_capture)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.setFixedWidth(120)
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)  # Set cursor in Python
        self.stop_btn.clicked.connect(self.stop_capture)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        return header
    
    def create_trades_tab(self):
        """Create the Today's Trades tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Info label
        info = QLabel("Best trading opportunities ranked by absolute profit potential")
        info.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        layout.addWidget(info)
        
        # Scroll area for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        # Container for cards
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(16)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll)
        
        return widget
    
    def create_history_tab(self):
        """Create the Price History tab with charts"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Product selector
        product_label = QLabel("Product:")
        product_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        controls_layout.addWidget(product_label)
        
        self.product_selector = QComboBox()
        self.product_selector.setMinimumWidth(300)
        self.product_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border_light']};
                border-radius: 6px;
                padding: 8px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                selection-background-color: {COLORS['accent_teal']};
            }}
        """)
        self.product_selector.currentTextChanged.connect(self.on_product_selected)
        controls_layout.addWidget(self.product_selector)
        
        # Time range selector
        range_label = QLabel("Time Range:")
        range_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        controls_layout.addWidget(range_label)
        
        self.range_selector = QComboBox()
        self.range_selector.addItems(["7 Days", "30 Days", "90 Days", "All Time"])
        self.range_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border_light']};
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        self.range_selector.currentTextChanged.connect(self.on_range_changed)
        controls_layout.addWidget(self.range_selector)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Chart area
        self.chart_widget = self.create_chart_widget()
        layout.addWidget(self.chart_widget, stretch=1)
        
        # Stats panel
        self.stats_panel = self.create_stats_panel()
        layout.addWidget(self.stats_panel)
        
        return widget
    
    def create_chart_widget(self):
        """Create the price history chart"""
        # Configure pyqtgraph for dark theme
        pg.setConfigOption('background', COLORS['bg_secondary'])
        pg.setConfigOption('foreground', COLORS['text_primary'])
        pg.setConfigOption('antialias', True)
        
        # Create plot widget
        plot = PlotWidget()
        plot.setMenuEnabled(False)
        plot.setMouseEnabled(x=True, y=True)
        plot.enableAutoRange(axis='x')
        plot.setLabel('left', 'Price', units='')
        plot.setLabel('bottom', 'Date', units='')
        plot.showGrid(x=True, y=True, alpha=0.3)
        
        # Style the axes
        axis_pen = mkPen(color=COLORS['text_secondary'], width=1)
        plot.getAxis('bottom').setPen(axis_pen)
        plot.getAxis('left').setPen(axis_pen)
        plot.getAxis('bottom').setTextPen(mkPen(color=COLORS['text_secondary']))
        plot.getAxis('left').setTextPen(mkPen(color=COLORS['text_secondary']))
        
        self.price_plot = plot
        
        return plot
    
    def create_stats_panel(self):
        """Create statistics panel below chart"""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        
        layout = QHBoxLayout(panel)
        layout.setSpacing(32)
        
        # Stats labels
        self.stat_labels = {}
        stats = [
            ('avg_price', 'Average Price', COLORS['text_primary']),
            ('max_diff', 'Max Difference', COLORS['success']),
            ('volatility', 'Volatility', COLORS['warning']),
            ('total_readings', 'Total Readings', COLORS['text_secondary']),
        ]
        
        for key, label, color in stats:
            stat_layout = QVBoxLayout()
            stat_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            title = QLabel(label)
            title.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
            stat_layout.addWidget(title)
            
            value = QLabel("--")
            value.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_layout.addWidget(value)
            
            self.stat_labels[key] = value
            layout.addLayout(stat_layout)
        
        layout.addStretch()
        
        return panel
    
    def apply_styles(self):
        """Apply application-wide styles"""
        self.setStyleSheet(get_main_stylesheet())
    
    def start_capture(self):
        """Start the capture session"""
        # Get selected monitor
        monitor_idx = self.monitor_selector.currentIndex() + 1
        
        # Visual feedback: Change button states
        self.start_btn.setEnabled(False)
        self.start_btn.setText("Running...")
        self.stop_btn.setEnabled(True)
        self.stop_btn.setText("Stop")
        
        # Change status indicator
        self.status_bar.showMessage("[CAPTURING] Screen capture active")
        success_color = COLORS['success']
        self.status_bar.setStyleSheet(f"color: {success_color}; font-weight: bold;")
        
        # Clear previous log
        self.screenshot_log.clear_log()
        self.screenshot_log.update_status("Starting capture...")
        
        # Create and start worker thread
        self.capture_worker = CaptureWorker(self.db_manager, monitor_idx=monitor_idx)
        self.capture_worker.status_update.connect(self.update_status)
        self.capture_worker.error_occurred.connect(self.show_error)
        self.capture_worker.product_captured.connect(self.on_product_captured)
        self.capture_worker.capture_count.connect(self.update_capture_count)
        self.capture_worker.screenshot_captured.connect(self.screenshot_log.add_screenshot)
        self.capture_worker.start()
        
        print("[OK] Capture started")

    def stop_capture(self):
        """Stop the capture session"""
        if self.capture_worker:
            self.capture_worker.stop()
            self.capture_worker = None
        
        # Visual feedback: Restore button states
        self.start_btn.setEnabled(True)
        self.start_btn.setText("Start")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setText("Stop")
        
        # Restore status bar
        self.status_bar.showMessage("Capture stopped - Data saved")
        text_secondary_color = COLORS['text_secondary']
        self.status_bar.setStyleSheet(f"color: {text_secondary_color};")
        
        self.screenshot_log.update_status("Capture stopped")
        
        # Refresh displays
        self.load_todays_data()
        self.load_price_history()
        
        print("[OK] Capture stopped")
    
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.showMessage(message)
    
    def update_capture_count(self, count):
        """Update the capture counter display"""
        self.capture_counter.setText(f"Captured: {count}")
    
    def show_error(self, error_msg):
        """Show error dialog"""
        QMessageBox.critical(self, "Error", error_msg)
        self.stop_capture()
    
    def on_product_captured(self, name, region, local_price, friend_price,   quantity_owned, average_cost, screenshot=None):
                         
        """Handle newly captured product"""
        # Add screenshot to log if provided
        if screenshot is not None:
            self.screenshot_log.add_screenshot(screenshot, f"Detected: {name}")
        
        # Update or create card
        if name in self.product_cards:
            card = self.product_cards[name]
            card.update_data(local_price, friend_price, quantity_owned, average_cost)
        else:
            # Create new card
            self.load_todays_data()
        
        # Update screenshot log status
        self.screenshot_log.update_status(f"Captured: {name} @ {local_price}")
    
    def load_todays_data(self):
        """Load today's captured data"""
        # Clear existing cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.product_cards.clear()
        
        # Get today's best opportunities
        readings = self.db_manager.get_best_opportunities_today()
        
        if not readings:
            # Show placeholder
            placeholder = QLabel("No data captured today.\n\nClick Start and browse your goods in-game.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet(f"""
                color: {COLORS['text_secondary']};
                font-size: 14px;
                padding: 40px;
            """)
            self.cards_layout.addWidget(placeholder, 0, 0, 1, 3)
            return
        
        # Add cards for each reading
        for i, reading in enumerate(readings):
            card = ProductCard(reading.product.name, reading.region)
            card.update_data(
                reading.local_price,
                reading.friend_price,
                reading.quantity_owned,
                reading.average_cost
            )
            
            # Highlight the best opportunity
            if i == 0 and reading.absolute_difference and reading.absolute_difference > 0:
                card.highlight_as_best()
            
            self.product_cards[reading.product.name] = card
            
            row = i // 3
            col = i % 3
            self.cards_layout.addWidget(card, row, col)
    
    def load_price_history(self):
        """Load products into history dropdown"""
        products = self.db_manager.get_all_products()
        
        current_selection = self.product_selector.currentText()
        
        self.product_selector.clear()
        self.product_selector.addItem("Select a product...")
        
        for product in sorted(products, key=lambda p: p.name):
            self.product_selector.addItem(product.name)
        
        # Restore selection if possible
        if current_selection and current_selection != "Select a product...":
            index = self.product_selector.findText(current_selection)
            if index >= 0:
                self.product_selector.setCurrentIndex(index)
    
    def on_product_selected(self, product_name):
        """Handle product selection change"""
        if not product_name or product_name == "Select a product...":
            return
        
        self.update_chart(product_name)
    
    def on_range_changed(self, range_text):
        """Handle time range change"""
        product_name = self.product_selector.currentText()
        if product_name and product_name != "Select a product...":
            self.update_chart(product_name)
    
    def update_chart(self, product_name: str):
        """Update the price history chart"""
        # Get time range
        range_text = self.range_selector.currentText()
        days_map = {
            "7 Days": 7,
            "30 Days": 30,
            "90 Days": 90,
            "All Time": 365 * 10  # 10 years effectively all time
        }
        days = days_map.get(range_text, 30)
        
        # Get data from database
        readings = self.db_manager.get_product_history(product_name, days)
        
        if not readings:
            self.price_plot.clear()
            self.update_stats(None)
            return
        
        # Prepare data for plotting
        import time
        from datetime import datetime
        
        timestamps = []
        local_prices = []
        friend_prices = []
        
        for r in readings:
            # Convert datetime to timestamp for plotting
            ts = time.mktime(r.timestamp.timetuple())
            timestamps.append(ts)
            local_prices.append(r.local_price)
            friend_prices.append(r.friend_price if r.friend_price else None)
        
        # Clear previous plots
        self.price_plot.clear()
        
        # Plot local prices
        if timestamps and local_prices:
            pen_local = mkPen(color=COLORS['accent_teal'], width=2)
            self.price_plot.plot(timestamps, local_prices, pen=pen_local, 
                                name="Local Price", symbol='o', symbolSize=6,
                                symbolBrush=mkBrush(color=COLORS['accent_teal']))
        
        # Plot friend prices
        friend_timestamps = [ts for ts, fp in zip(timestamps, friend_prices) if fp]
        friend_prices_filtered = [fp for fp in friend_prices if fp]
        
        if friend_timestamps and friend_prices_filtered:
            pen_friend = mkPen(color=COLORS['success'], width=2)
            self.price_plot.plot(friend_timestamps, friend_prices_filtered, 
                                pen=pen_friend, name="Friend Price", 
                                symbol='s', symbolSize=6,
                                symbolBrush=mkBrush(color=COLORS['success']))
        
        # Add legend
        self.price_plot.addLegend()
        
        # Update stats
        stats = self.db_manager.get_price_stats(product_name)
        self.update_stats(stats)
    
    def update_stats(self, stats):
        """Update statistics panel"""
        if not stats:
            for label in self.stat_labels.values():
                label.setText("--")
            return
        
        self.stat_labels['avg_price'].setText(f"{stats.get('avg_local_price', 0):,.0f}")
        self.stat_labels['max_diff'].setText(f"{stats.get('max_difference', 0):,}")
        
        # Calculate volatility as percentage
        avg_price = stats.get('avg_local_price', 0)
        price_range = stats.get('max_difference', 0)
        volatility = (price_range / avg_price * 100) if avg_price > 0 else 0
        self.stat_labels['volatility'].setText(f"{volatility:.1f}%")
        
        self.stat_labels['total_readings'].setText(str(stats.get('total_readings', 0)))
    
    def refresh_data(self):
        """Auto-refresh data when capture is running"""
        if self.capture_worker and self.capture_worker.running:
            self.load_todays_data()
            
            # Also refresh chart if a product is selected
            product_name = self.product_selector.currentText()
            if product_name and product_name != "Select a product...":
                self.update_chart(product_name)
    
    def closeEvent(self, event):
        """Clean up on close"""
        if self.capture_worker and self.capture_worker.running:
            self.capture_worker.stop()
        
        self.db_manager.close()
        event.accept()