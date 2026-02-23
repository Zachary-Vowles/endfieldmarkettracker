"""
Stylesheet definitions for Endfield Market Tracker
Matches the game's sci-fi aesthetic
"""

from src.utils.constants import COLORS

def get_main_stylesheet():
    """Returns the main application stylesheet"""
    return f"""
    QMainWindow {{
        background-color: {COLORS['bg_primary']};
        color: {COLORS['text_primary']};
        font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
    }}
    
    QWidget {{
        background-color: {COLORS['bg_primary']};
        color: {COLORS['text_primary']};
    }}
    
    /* Tab Widget Styling */
    QTabWidget::pane {{
        border: 1px solid {COLORS['border_light']};
        border-radius: 8px;
        background-color: {COLORS['bg_secondary']};
        top: -1px;
    }}
    
    QTabBar::tab {{
        background-color: {COLORS['bg_card']};
        color: {COLORS['text_secondary']};
        padding: 12px 24px;
        margin-right: 4px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-weight: 500;
        font-size: 13px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_primary']};
        border-top: 2px solid {COLORS['accent_teal']};
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {COLORS['bg_card_hover']};
        color: {COLORS['text_primary']};
    }}
    
    /* Button Styling */
    QPushButton {{
        border: none;
        border-radius: 20px;
        padding: 12px 32px;
        font-weight: 600;
        font-size: 14px;
        cursor: pointer;
    }}
    
    QPushButton#startButton {{
        background-color: {COLORS['button_start']};
        color: {COLORS['bg_primary']};
    }}
    
    QPushButton#startButton:hover {{
        background-color: {COLORS['button_start_hover']};
    }}
    
    QPushButton#startButton:pressed {{
        background-color: #e0e0e0;
    }}
    
    QPushButton#stopButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
            stop:0 {COLORS['button_stop_start']}, 
            stop:1 {COLORS['button_stop_end']});
        color: white;
    }}
    
    QPushButton#stopButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
            stop:0 #ff8585, 
            stop:1 #f07070);
    }}
    
    QPushButton#stopButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
            stop:0 #e05555, 
            stop:1 #d04040);
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS['bg_card']};
        color: {COLORS['text_disabled']};
    }}
    
    /* Card Styling */
    QFrame#productCard {{
        background-color: {COLORS['bg_card']};
        border-radius: 12px;
        border: 1px solid {COLORS['border_light']};
    }}
    
    QFrame#productCard:hover {{
        background-color: {COLORS['bg_card_hover']};
        border: 1px solid {COLORS['border_highlight']};
    }}
    
    /* Labels */
    QLabel {{
        color: {COLORS['text_primary']};
    }}
    
    QLabel#productName {{
        font-size: 16px;
        font-weight: 600;
        color: {COLORS['text_primary']};
    }}
    
    QLabel#priceLabel {{
        font-size: 24px;
        font-weight: 700;
        color: {COLORS['accent_teal']};
    }}
    
    QLabel#profitPositive {{
        color: {COLORS['success']};
        font-weight: 600;
    }}
    
    QLabel#profitNegative {{
        color: {COLORS['danger']};
        font-weight: 600;
    }}
    
    QLabel#secondaryText {{
        color: {COLORS['text_secondary']};
        font-size: 12px;
    }}
    
    /* Scroll Area */
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    
    QScrollBar:vertical {{
        background-color: {COLORS['bg_secondary']};
        width: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS['border_light']};
        border-radius: 6px;
        min-height: 30px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['text_secondary']};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    /* Status Bar */
    QStatusBar {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_secondary']};
        border-top: 1px solid {COLORS['border_light']};
    }}
    
    /* Group Box */
    QGroupBox {{
        background-color: {COLORS['bg_card']};
        border: 1px solid {COLORS['border_light']};
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 12px;
        font-weight: 600;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px;
        color: {COLORS['text_secondary']};
    }}
"""

def get_header_style():
    """Style for the header section"""
    return f"""
    background-color: {COLORS['bg_secondary']};
    border-bottom: 1px solid {COLORS['border_light']};
    padding: 16px;
"""

def get_card_style():
    """Style for product cards"""
    return f"""
    background-color: {COLORS['bg_card']};
    border-radius: 12px;
    border: 1px solid {COLORS['border_light']};
    padding: 16px;
"""