"""
Product card widget for displaying trade opportunities
"""

from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                             QWidget, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from src.utils.constants import COLORS, CURRENCIES, Region

class ProductCard(QFrame):
    
    def __init__(self, product_name: str, region: str, parent=None):
        super().__init__(parent)
        self.product_name = product_name
        self.region = Region(region) if isinstance(region, str) else region
        self.setObjectName("productCard")
        # WIDENED CARD to prevent clipping
        self.setFixedSize(360, 220) 
        self.setup_ui()
        self.apply_shadow()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        self.name_label = QLabel(self.product_name)
        self.name_label.setObjectName("productName")
        self.name_label.setWordWrap(True)
        header_layout.addWidget(self.name_label, stretch=1)
        
        currency = CURRENCIES.get(self.region, "HZ")
        self.currency_label = QLabel(currency)
        pill_color = COLORS['accent_teal'] if self.region == Region.WULING else COLORS['accent_yellow']
        text_color = "#ffffff" if self.region == Region.WULING else "#000000"
        self.currency_label.setStyleSheet(f"color: {text_color}; font-weight: 700; font-size: 12px; padding: 4px 10px; background-color: {pill_color}; border-radius: 12px;")
        header_layout.addWidget(self.currency_label)
        layout.addLayout(header_layout)
        
        # Price section
        price_layout = QHBoxLayout()
        
        local_layout = QVBoxLayout()
        local_title = QLabel("Local Price")
        local_title.setObjectName("secondaryText")
        local_layout.addWidget(local_title)
        self.local_price_label = QLabel("--")
        self.local_price_label.setMinimumWidth(80) # Prevent clipping
        self.local_price_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 18px; font-weight: 700;")
        local_layout.addWidget(self.local_price_label)
        price_layout.addLayout(local_layout)
        
        price_layout.addStretch()
        
        friend_layout = QVBoxLayout()
        friend_title = QLabel("Friend Price")
        friend_title.setObjectName("secondaryText")
        friend_layout.addWidget(friend_title)
        self.friend_price_label = QLabel("--")
        self.friend_price_label.setMinimumWidth(80) # Prevent clipping
        self.friend_price_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.friend_price_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 18px; font-weight: 700;")
        friend_layout.addWidget(self.friend_price_label)
        price_layout.addLayout(friend_layout)
        
        layout.addLayout(price_layout)
        
        # Profit per unit indicator
        profit_layout = QHBoxLayout()
        profit_title = QLabel("Unit Profit:")
        profit_title.setObjectName("secondaryText")
        profit_layout.addWidget(profit_title)
        profit_layout.addStretch()
        
        self.profit_label = QLabel("--")
        self.profit_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 22px; font-weight: 800;")
        profit_layout.addWidget(self.profit_label)
        layout.addLayout(profit_layout)

        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet(f"background-color: {COLORS['border_light']}; max-height: 1px;")
        layout.addWidget(line)
        
        # Footer
        total_layout = QHBoxLayout()
        self.owned_label = QLabel("Owned: 0")
        self.owned_label.setObjectName("secondaryText")
        total_layout.addWidget(self.owned_label)
        total_layout.addStretch()

        self.total_profit_label = QLabel("Total Potential: --")
        self.total_profit_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 700; font-size: 14px;")
        total_layout.addWidget(self.total_profit_label)
        layout.addLayout(total_layout)
    
    def apply_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def update_data(self, local_price: int, friend_price: int, quantity_owned: int = 0, average_cost: int = None):
        currency = CURRENCIES.get(self.region, "HZ")
        self.local_price_label.setText(f"{local_price:,}" if local_price else "--")
        
        profit_per_unit = 0
        if friend_price and local_price:
            self.friend_price_label.setText(f"{friend_price:,}")
            profit_per_unit = friend_price - local_price
            
            if profit_per_unit > 0:
                self.profit_label.setText(f"+{profit_per_unit:,}")
                self.profit_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 22px; font-weight: 800;")
            else:
                self.profit_label.setText(f"{profit_per_unit:,}")
                self.profit_label.setStyleSheet(f"color: {COLORS['danger']}; font-size: 22px; font-weight: 800;")
        else:
            self.friend_price_label.setText("--")
            self.profit_label.setText("--")
            self.profit_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 22px; font-weight: 800;")
        
        self.owned_label.setText(f"Owned: {quantity_owned}")
        
        if quantity_owned > 0 and profit_per_unit != 0:
            total_profit = profit_per_unit * quantity_owned
            sign = "+" if total_profit > 0 else ""
            self.total_profit_label.setText(f"Total: {sign}{total_profit:,} {currency}")
            self.total_profit_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 700;")
        else:
            self.total_profit_label.setText("Total: --")
            self.total_profit_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 700;")

    def highlight_as_best(self):
        self.setStyleSheet(f"QFrame#productCard {{ background-color: {COLORS['bg_card']}; border-radius: 12px; border: 2px solid {COLORS['accent_yellow']}; }}")
    
    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().enterEvent(event)
    def leaveEvent(self, event):
        self.unsetCursor()
        super().leaveEvent(event)