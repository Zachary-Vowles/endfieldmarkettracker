"""
Main application window for Endfield Market Tracker
Updated with Endfield light/dark composite aesthetics
"""

import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTabWidget, QScrollArea, 
                             QGridLayout, QFrame, QStatusBar, QMessageBox,
                             QComboBox)
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
        self.capture_worker = None
        self.product_cards = {}
        
        self.setup_ui()
        self.apply_styles()
        
        self.load_todays_data()
        self.load_price_history()
        
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(5000)
    
    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Outer layout (Dark background)
        outer_layout = QHBoxLayout(central_widget)
        outer_layout.setContentsMargins(20, 20, 20, 20)
        outer_layout.setSpacing(20)
        
        # The Main "Light" Panel from the Mockup
        self.main_panel = QFrame()
        self.main_panel.setObjectName("mainPanel")
        
        # Drop shadow for the panel
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 8)
        self.main_panel.setGraphicsEffect(shadow)

        panel_layout = QVBoxLayout(self.main_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        panel_layout.addWidget(header)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        
        self.trades_tab = self.create_trades_tab()
        self.tab_widget.addTab(self.trades_tab, "Today's Trades")
        
        self.history_tab = self.create_history_tab()
        self.tab_widget.addTab(self.history_tab, "Price History")
        
        panel_layout.addWidget(self.tab_widget, stretch=1)
        
        # Add main panel to left side
        outer_layout.addWidget(self.main_panel, stretch=1)
        
        # Right side - Screenshot log (Dark)
        self.screenshot_log = ScreenshotLogWidget()
        outer_layout.addWidget(self.screenshot_log)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Click Start and browse your goods in-game")

    def create_header(self):
        """Create the header section with controls"""
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(90)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(32, 12, 32, 12)
        
        # Title area
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        title = QLabel("Tracker Controls")
        title.setObjectName("titleLabel")
        title_layout.addWidget(title)
        
        subtitle = QLabel("// Market Tracker Ready")
        subtitle.setObjectName("subtitleLabel")
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Capture counter
        self.capture_counter = QLabel("Captured: 0")
        self.capture_counter.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px; font-weight: 600; padding-right: 24px;")
        layout.addWidget(self.capture_counter)
        
        # Monitor selector
        self.monitor_selector = QComboBox()
        self.monitor_selector.setMinimumWidth(160)
        
        from src.core.screen_capture import ScreenCapture
        temp_capture = ScreenCapture.__new__(ScreenCapture)
        temp_capture.sct = __import__('mss').mss()
        temp_capture.monitors = temp_capture.sct.monitors
        for i in range(1, len(temp_capture.monitors)):
            mon = temp_capture.monitors[i]
            self.monitor_selector.addItem(f"Monitor {i}: {mon['width']}x{mon['height']}")
        temp_capture.sct.close()
        
        layout.addWidget(self.monitor_selector)
        layout.addSpacing(20)

        # Calibrate Button
        calibrate_btn = QPushButton("Calibrate")
        calibrate_btn.setObjectName("outlineButton")
        calibrate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        calibrate_btn.clicked.connect(self.open_calibration)
        layout.addWidget(calibrate_btn)
        layout.addSpacing(12)

        # Control buttons
        self.start_btn = QPushButton("Start Capture")
        self.start_btn.setObjectName("startButton")
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.clicked.connect(self.start_capture)
        layout.addWidget(self.start_btn)
        layout.addSpacing(8)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.clicked.connect(self.stop_capture)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        return header

    def open_calibration(self):
        from src.ui.calibration_wizard import CalibrationWizard
        wizard = CalibrationWizard(self)
        wizard.exec()

    def create_trades_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)
        
        info = QLabel("Best trading opportunities ranked by absolute profit potential")
        info.setObjectName("subtitleLabel")
        layout.addWidget(info)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(20)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll)
        return widget
    
    def create_history_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(20)
        
        controls_layout = QHBoxLayout()
        
        self.product_selector = QComboBox()
        self.product_selector.setMinimumWidth(300)
        self.product_selector.currentTextChanged.connect(self.on_product_selected)
        controls_layout.addWidget(self.product_selector)
        
        controls_layout.addSpacing(20)
        
        self.range_selector = QComboBox()
        self.range_selector.addItems(["7 Days", "30 Days", "90 Days", "All Time"])
        self.range_selector.currentTextChanged.connect(self.on_range_changed)
        controls_layout.addWidget(self.range_selector)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        self.chart_widget = self.create_chart_widget()
        layout.addWidget(self.chart_widget, stretch=1)
        
        self.stats_panel = self.create_stats_panel()
        layout.addWidget(self.stats_panel)
        
        return widget
    
    def create_chart_widget(self):
        # Configure pyqtgraph for light theme to match the panel
        pg.setConfigOption('background', COLORS['bg_card'])
        pg.setConfigOption('foreground', COLORS['text_primary'])
        pg.setConfigOption('antialias', True)
        
        plot = PlotWidget()
        plot.setMenuEnabled(False)
        plot.setMouseEnabled(x=True, y=True)
        plot.enableAutoRange(axis='x')
        plot.setLabel('left', 'Price', units='')
        plot.setLabel('bottom', 'Date', units='')
        plot.showGrid(x=True, y=True, alpha=0.15)
        
        axis_pen = mkPen(color=COLORS['border_light'], width=1)
        plot.getAxis('bottom').setPen(axis_pen)
        plot.getAxis('left').setPen(axis_pen)
        plot.getAxis('bottom').setTextPen(mkPen(color=COLORS['text_secondary']))
        plot.getAxis('left').setTextPen(mkPen(color=COLORS['text_secondary']))
        
        self.price_plot = plot
        return plot
    
    def create_stats_panel(self):
        panel = QFrame()
        panel.setObjectName("productCard") # Reuse card styling
        panel.setMinimumHeight(100)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(40)
        
        self.stat_labels = {}
        stats = [
            ('avg_price', 'Average Price', COLORS['text_primary']),
            ('max_diff', 'Max Difference', COLORS['success']),
            ('volatility', 'Volatility', COLORS['danger']),
            ('total_readings', 'Total Readings', COLORS['text_secondary']),
        ]
        
        for key, label, color in stats:
            stat_layout = QVBoxLayout()
            stat_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            title = QLabel(label)
            title.setObjectName("subtitleLabel")
            stat_layout.addWidget(title)
            
            value = QLabel("--")
            value.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 700;")
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_layout.addWidget(value)
            
            self.stat_labels[key] = value
            layout.addLayout(stat_layout)
            
        layout.addStretch()
        return panel
    
    def apply_styles(self):
        self.setStyleSheet(get_main_stylesheet())
    
    def start_capture(self):
        monitor_idx = self.monitor_selector.currentIndex() + 1
        self.start_btn.setEnabled(False)
        self.start_btn.setText("Running...")
        self.stop_btn.setEnabled(True)
        
        self.status_bar.showMessage("[CAPTURING] Screen capture active")
        
        self.screenshot_log.clear_log()
        self.screenshot_log.update_status("Starting capture...")
        
        self.capture_worker = CaptureWorker(self.db_manager, monitor_idx=monitor_idx)
        self.capture_worker.status_update.connect(self.update_status)
        self.capture_worker.error_occurred.connect(self.show_error)
        self.capture_worker.product_captured.connect(self.on_product_captured)
        self.capture_worker.capture_count.connect(self.update_capture_count)
        self.capture_worker.screenshot_captured.connect(self.screenshot_log.add_screenshot)
        self.capture_worker.start()
        
    def stop_capture(self):
        if self.capture_worker:
            self.capture_worker.stop()
            self.capture_worker = None
            
        self.start_btn.setEnabled(True)
        self.start_btn.setText("Start Capture")
        self.stop_btn.setEnabled(False)
        
        self.status_bar.showMessage("Capture stopped - Data saved")
        self.screenshot_log.update_status("Capture stopped")
        
        self.load_todays_data()
        self.load_price_history()
    
    def update_status(self, message):
        self.status_bar.showMessage(message)
    
    def update_capture_count(self, count):
        self.capture_counter.setText(f"Captured: {count}")
    
    def show_error(self, error_msg):
        QMessageBox.critical(self, "Error", error_msg)
        self.stop_capture()
    
    def on_product_captured(self, name, region, local_price, friend_price, quantity_owned, average_cost, screenshot=None):
        if screenshot is not None:
            self.screenshot_log.add_screenshot(screenshot, f"Detected: {name}")
        
        if name in self.product_cards:
            card = self.product_cards[name]
            card.update_data(local_price, friend_price, quantity_owned, average_cost)
        else:
            self.load_todays_data()
            
        self.screenshot_log.update_status(f"Captured: {name} @ {local_price}")
    
    def load_todays_data(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        self.product_cards.clear()
        readings = self.db_manager.get_best_opportunities_today()
        
        if not readings:
            placeholder = QLabel("No data captured today.\n\nClick Start Capture and browse your goods in-game.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet(f"color: {COLORS['text_disabled']}; font-size: 16px; font-weight: 500; padding: 60px;")
            self.cards_layout.addWidget(placeholder, 0, 0, 1, 3)
            return
            
        for i, reading in enumerate(readings):
            card = ProductCard(reading.product.name, reading.region)
            card.update_data(
                reading.local_price,
                reading.friend_price,
                reading.quantity_owned,
                reading.average_cost
            )
            
            if i == 0 and reading.absolute_difference and reading.absolute_difference > 0:
                card.highlight_as_best()
                
            self.product_cards[reading.product.name] = card
            row = i // 3
            col = i % 3
            self.cards_layout.addWidget(card, row, col)
    
    def load_price_history(self):
        products = self.db_manager.get_all_products()
        current_selection = self.product_selector.currentText()
        
        self.product_selector.clear()
        self.product_selector.addItem("Select a product...")
        
        for product in sorted(products, key=lambda p: p.name):
            self.product_selector.addItem(product.name)
            
        if current_selection and current_selection != "Select a product...":
            index = self.product_selector.findText(current_selection)
            if index >= 0:
                self.product_selector.setCurrentIndex(index)
    
    def on_product_selected(self, product_name):
        if not product_name or product_name == "Select a product...":
            return
        self.update_chart(product_name)
    
    def on_range_changed(self, range_text):
        product_name = self.product_selector.currentText()
        if product_name and product_name != "Select a product...":
            self.update_chart(product_name)
    
    def update_chart(self, product_name: str):
        range_text = self.range_selector.currentText()
        days_map = { "7 Days": 7, "30 Days": 30, "90 Days": 90, "All Time": 365 * 10 }
        days = days_map.get(range_text, 30)
        
        readings = self.db_manager.get_product_history(product_name, days)
        
        if not readings:
            self.price_plot.clear()
            self.update_stats(None)
            return
            
        import time
        timestamps, local_prices, friend_prices = [], [], []
        
        for r in readings:
            ts = time.mktime(r.timestamp.timetuple())
            timestamps.append(ts)
            local_prices.append(r.local_price)
            friend_prices.append(r.friend_price if r.friend_price else None)
            
        self.price_plot.clear()
        
        if timestamps and local_prices:
            pen_local = mkPen(color=COLORS['text_disabled'], width=3)
            self.price_plot.plot(timestamps, local_prices, pen=pen_local, 
                                name="Local Price", symbol='o', symbolSize=8,
                                symbolBrush=mkBrush(color=COLORS['text_secondary']))
                                
        friend_timestamps = [ts for ts, fp in zip(timestamps, friend_prices) if fp]
        friend_prices_filtered = [fp for fp in friend_prices if fp]
        
        if friend_timestamps and friend_prices_filtered:
            pen_friend = mkPen(color=COLORS['accent_yellow'], width=3)
            self.price_plot.plot(friend_timestamps, friend_prices_filtered, 
                                pen=pen_friend, name="Friend Price", 
                                symbol='o', symbolSize=8,
                                symbolBrush=mkBrush(color=COLORS['accent_yellow']))
                                
        self.price_plot.addLegend()
        stats = self.db_manager.get_price_stats(product_name)
        self.update_stats(stats)
    
    def update_stats(self, stats):
        if not stats:
            for label in self.stat_labels.values():
                label.setText("--")
            return
            
        self.stat_labels['avg_price'].setText(f"{stats.get('avg_local_price', 0):,.0f}")
        self.stat_labels['max_diff'].setText(f"{stats.get('max_difference', 0):,}")
        
        avg_price = stats.get('avg_local_price', 0)
        price_range = stats.get('max_difference', 0)
        volatility = (price_range / avg_price * 100) if avg_price > 0 else 0
        self.stat_labels['volatility'].setText(f"{volatility:.1f}%")
        self.stat_labels['total_readings'].setText(str(stats.get('total_readings', 0)))
    
    def refresh_data(self):
        if self.capture_worker and self.capture_worker.running:
            self.load_todays_data()
            product_name = self.product_selector.currentText()
            if product_name and product_name != "Select a product...":
                self.update_chart(product_name)
                
    def closeEvent(self, event):
        if self.capture_worker and self.capture_worker.running:
            self.capture_worker.stop()
        self.db_manager.close()
        event.accept()