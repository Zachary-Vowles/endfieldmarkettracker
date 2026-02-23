"""
Product card widget for displaying trade opportunities
"""

from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                             QWidget, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
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
        """Setup the card UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Header: Product name and region indicator
        header_layout = QHBoxLayout()
        
        self.name_label = QLabel(self.product_name)
        self.name_label.setObjectName("productName")
        self.name_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.name_label.setWordWrap(True)
        header_layout.addWidget(self.name_label, stretch=1)
        
        # Region/currency indicator
        currency = CURRENCIES.get(self.region, "HZ")
        self.currency_label = QLabel(currency)
        self.currency_label.setStyleSheet(f"""
            color: {COLORS['accent_teal'] if self.region == Region.WULING else COLORS['accent_yellow']};
            font-weight: bold;
            font-size: 12px;
            padding: 4px 8px;
            background-color: {COLORS['bg_secondary']};
            border-radius: 4px;
        """)
        header_layout.addWidget(self.currency_label)
        
        layout.addLayout(header_layout)
        
        # Price section
        price_layout = QHBoxLayout()
        
        # Local price
        local_layout = QVBoxLayout()
        local_title = QLabel("Local Price")
        local_title.setObjectName("secondaryText")
        local_title.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        local_layout.addWidget(local_title)
        
        self.local_price_label = QLabel("--")
        self.local_price_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 20px;
            font-weight: 600;
        """)
        local_layout.addWidget(self.local_price_label)
        price_layout.addLayout(local_layout)
        
        price_layout.addStretch()
        
        # Friend price
        friend_layout = QVBoxLayout()
        friend_title = QLabel("Friend Price")
        friend_title.setObjectName("secondaryText")
        friend_title.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        friend_layout.addWidget(friend_title)
        
        self.friend_price_label = QLabel("--")
        self.friend_price_label.setStyleSheet(f"""
            color: {COLORS['success']};
            font-size: 20px;
            font-weight: 600;
        """)
        friend_layout.addWidget(self.friend_price_label)
        price_layout.addLayout(friend_layout)
        
        layout.addLayout(price_layout)
        
        # Profit indicator (main highlight)
        profit_layout = QHBoxLayout()
        profit_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.profit_label = QLabel("+")
        self.profit_label.setStyleSheet(f"""
            color: {COLORS['success']};
            font-size: 32px;
            font-weight: 700;
        """)
        profit_layout.addWidget(self.profit_label)
        
        layout.addLayout(profit_layout)
        
        # Additional info
        info_layout = QHBoxLayout()
        
        self.owned_label = QLabel("Owned: 0")
        self.owned_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        info_layout.addWidget(self.owned_label)
        
        info_layout.addStretch()
        
        self.avg_cost_label = QLabel("Avg: --")
        self.avg_cost_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        info_layout.addWidget(self.avg_cost_label)
        
        layout.addLayout(info_layout)
        
        # Set card style
        self.setStyleSheet(f"""
            ProductCard {{
                background-color: {COLORS['bg_card']};
                border-radius: 12px;
                border: 1px solid {COLORS['border_light']};
            }}
            ProductCard:hover {{
                background-color: {COLORS['bg_card_hover']};
                border: 1px solid {COLORS['accent_teal']};
            }}
        """)
    
    def apply_shadow(self):
        """Apply drop shadow effect"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def update_data(self, local_price: int, friend_price: int, 
                   quantity_owned: int = 0, average_cost: int = None):
        """Update the card with new price data"""
        currency = CURRENCIES.get(self.region, "HZ")
        
        self.local_price_label.setText(f"{local_price:,} {currency}")
        
        if friend_price:
            self.friend_price_label.setText(f"{friend_price:,} {currency}")
            profit = friend_price - local_price
            
            # Update profit display
            if profit > 0:
                self.profit_label.setText(f"+{profit:,}")
                self.profit_label.setStyleSheet(f"""
                    color: {COLORS['success']};
                    font-size: 32px;
                    font-weight: 700;
                """)
            elif profit < 0:
                self.profit_label.setText(f"{profit:,}")
                self.profit_label.setStyleSheet(f"""
                    color: {COLORS['danger']};
                    font-size: 32px;
                    font-weight: 700;
                """)
            else:
                self.profit_label.setText("0")
                self.profit_label.setStyleSheet(f"""
                    color: {COLORS['text_secondary']};
                    font-size: 32px;
                    font-weight: 700;
                """)
        else:
            self.friend_price_label.setText("--")
            self.profit_label.setText("--")
        
        # Update owned info
        self.owned_label.setText(f"Owned: {quantity_owned}")
        
        if average_cost and quantity_owned > 0:
            self.avg_cost_label.setText(f"Avg: {average_cost:,}")
        else:
            self.avg_cost_label.setText("Avg: --")
    
    def highlight_as_best(self):
        """Highlight this card as the best opportunity"""
        self.setStyleSheet(f"""
            ProductCard {{
                background-color: {COLORS['bg_card']};
                border-radius: 12px;
                border: 2px solid {COLORS['success']};
            }}
        """)
    
    def enterEvent(self, event):
        """Hover effect"""
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Remove hover effect"""
        self.unsetCursor()
        super().leaveEvent(event)