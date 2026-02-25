"""
Product card widget for displaying trade opportunities
Clean light theme based on Endfield aesthetic
"""

from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                             QWidget, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from src.utils.constants import COLORS, CURRENCIES, Region

class ProductCard(QFrame):
    """A card displaying product information and trading opportunity"""
    
    def __init__(self, product_name: str, region: str, parent=None):
        super().__init__(parent)
        self.product_name = product_name
        self.region = Region(region) if isinstance(region, str) else region
        self.setObjectName("productCard")
        self.setFixedSize(320, 180)
        self.setup_ui()
        self.apply_shadow()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        
        # Header: Product name and region indicator
        header_layout = QHBoxLayout()
        
        self.name_label = QLabel(self.product_name)
        self.name_label.setObjectName("productName")
        self.name_label.setWordWrap(True)
        header_layout.addWidget(self.name_label, stretch=1)
        
        # Region/currency indicator pill
        currency = CURRENCIES.get(self.region, "HZ")
        self.currency_label = QLabel(currency)
        pill_color = COLORS['accent_teal'] if self.region == Region.WULING else COLORS['accent_yellow']
        text_color = "#ffffff" if self.region == Region.WULING else "#000000"
        
        self.currency_label.setStyleSheet(f"""
            color: {text_color};
            font-weight: 700;
            font-size: 12px;
            padding: 4px 10px;
            background-color: {pill_color};
            border-radius: 12px;
        """)
        header_layout.addWidget(self.currency_label)
        
        layout.addLayout(header_layout)
        
        # Price section
        price_layout = QHBoxLayout()
        
        local_layout = QVBoxLayout()
        local_title = QLabel("Local Price")
        local_title.setObjectName("secondaryText")
        local_layout.addWidget(local_title)
        
        self.local_price_label = QLabel("--")
        self.local_price_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 20px; font-weight: 700;")
        local_layout.addWidget(self.local_price_label)
        price_layout.addLayout(local_layout)
        
        price_layout.addStretch()
        
        friend_layout = QVBoxLayout()
        friend_title = QLabel("Friend Price")
        friend_title.setObjectName("secondaryText")
        friend_layout.addWidget(friend_title)
        
        self.friend_price_label = QLabel("--")
        self.friend_price_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 20px; font-weight: 700;")
        friend_layout.addWidget(self.friend_price_label)
        price_layout.addLayout(friend_layout)
        
        layout.addLayout(price_layout)
        
        # Profit indicator
        profit_layout = QHBoxLayout()
        profit_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.profit_label = QLabel("+")
        self.profit_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 28px; font-weight: 800;")
        profit_layout.addWidget(self.profit_label)
        
        layout.addLayout(profit_layout)
        
        # Footer
        info_layout = QHBoxLayout()
        
        self.owned_label = QLabel("Owned: 0")
        self.owned_label.setObjectName("secondaryText")
        info_layout.addWidget(self.owned_label)
        
        info_layout.addStretch()
        
        self.avg_cost_label = QLabel("Avg: --")
        self.avg_cost_label.setObjectName("secondaryText")
        info_layout.addWidget(self.avg_cost_label)
        
        layout.addLayout(info_layout)
    
    def apply_shadow(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def update_data(self, local_price: int, friend_price: int, quantity_owned: int = 0, average_cost: int = None):
        currency = CURRENCIES.get(self.region, "HZ")
        self.local_price_label.setText(f"{local_price:,} {currency}")
        
        if friend_price:
            self.friend_price_label.setText(f"{friend_price:,} {currency}")
            profit = friend_price - local_price
            
            if profit > 0:
                self.profit_label.setText(f"+{profit:,}")
                self.profit_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 28px; font-weight: 800;")
            elif profit < 0:
                self.profit_label.setText(f"{profit:,}")
                self.profit_label.setStyleSheet(f"color: {COLORS['danger']}; font-size: 28px; font-weight: 800;")
            else:
                self.profit_label.setText("0")
                self.profit_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 28px; font-weight: 800;")
        else:
            self.friend_price_label.setText("--")
            self.profit_label.setText("--")
        
        self.owned_label.setText(f"Owned: {quantity_owned}")
        if average_cost and quantity_owned > 0:
            self.avg_cost_label.setText(f"Avg: {average_cost:,}")
        else:
            self.avg_cost_label.setText("Avg: --")
    
    def highlight_as_best(self):
        self.setStyleSheet(f"""
            QFrame#productCard {{
                background-color: {COLORS['bg_card']};
                border-radius: 12px;
                border: 2px solid {COLORS['accent_yellow']};
            }}
        """)
    
    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.unsetCursor()
        super().leaveEvent(event)