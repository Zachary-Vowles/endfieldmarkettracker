"""
Stylesheet definitions for Endfield Market Tracker
Matches the game's clean, frosted sci-fi aesthetic
"""

from src.utils.constants import COLORS

def get_main_stylesheet():
    """Returns the main application stylesheet"""
    return f"""
    /* Main Window Background (The dark environment behind the popup) */
    QMainWindow {{
        background-color: {COLORS['bg_app']};
    }}
    
    QWidget {{
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }}
    
    /* Central Main Panel (The frosted white 'popup' window) */
    QFrame#mainPanel {{
        background-color: {COLORS['bg_panel']};
        border-radius: 8px;
        border: 1px solid {COLORS['border_dark']};
    }}
    
    /* Header Area */
    QFrame#header {{
        background-color: {COLORS['bg_header']};
        border-bottom: 1px solid {COLORS['border_light']};
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }}
    
    /* Tab Widget Styling */
    QTabWidget::pane {{
        border: none;
        background-color: transparent;
    }}
    
    QTabBar::tab {{
        background-color: transparent;
        color: {COLORS['text_secondary']};
        padding: 12px 24px;
        margin-right: 8px;
        font-weight: 600;
        font-size: 14px;
        border-bottom: 3px solid transparent;
    }}
    
    QTabBar::tab:selected {{
        color: {COLORS['text_primary']};
        border-bottom: 3px solid {COLORS['accent_yellow']};
    }}
    
    QTabBar::tab:hover:!selected {{
        color: {COLORS['text_primary']};
    }}
    
    /* General Button Styling (Pill Shapes) */
    QPushButton {{
        border: none;
        border-radius: 20px; /* Extreme border radius for the pill look */
        padding: 12px 28px;
        font-weight: 600;
        font-size: 14px;
    }}
    
    /* START BUTTON */
    QPushButton#startButton {{
        background-color: {COLORS['btn_start_bg']};
        color: {COLORS['btn_start_text']};
        border: 1px solid {COLORS['border_light']};
    }}
    
    QPushButton#startButton:hover {{
        background-color: #f9fafb;
        border: 1px solid #9ca3af;
    }}
    
    QPushButton#startButton:pressed {{
        background-color: #e5e7eb;
        padding-top: 14px; /* Simulates the active:scale-95 push down effect */
        padding-bottom: 10px;
    }}
    
    /* STOP BUTTON */
    QPushButton#stopButton {{
        background-color: {COLORS['btn_stop_bg']};
        color: {COLORS['text_inverse']};
    }}
    
    QPushButton#stopButton:hover {{
        background-color: {COLORS['btn_stop_hover']};
    }}
    
    QPushButton#stopButton:pressed {{
        background-color: #111111;
        padding-top: 14px;
        padding-bottom: 10px;
    }}

    /* ACTION BUTTON (Endfield Yellow) */
    QPushButton#actionButton {{
        background-color: {COLORS['accent_yellow']};
        color: #000000;
    }}
    QPushButton#actionButton:hover {{
        background-color: {COLORS['accent_yellow_hover']};
    }}
    QPushButton#actionButton:pressed {{
        padding-top: 14px;
        padding-bottom: 10px;
    }}

    /* OUTLINE BUTTON (E.g. Calibrate) */
    QPushButton#outlineButton {{
        background-color: transparent;
        color: {COLORS['text_primary']};
        border: 2px solid {COLORS['btn_outline_border']};
    }}
    QPushButton#outlineButton:hover {{
        background-color: {COLORS['border_light']};
    }}
    QPushButton#outlineButton:pressed {{
        padding-top: 14px;
        padding-bottom: 10px;
    }}
    
    QPushButton:disabled {{
        background-color: #e5e7eb;
        color: {COLORS['text_disabled']};
        border: none;
    }}
    
    /* Card Styling */
    QFrame#productCard {{
        background-color: {COLORS['bg_card']};
        border-radius: 12px;
        border: 1px solid {COLORS['border_light']};
    }}
    
    QFrame#productCard:hover {{
        background-color: {COLORS['bg_card_hover']};
        border: 1px solid {COLORS['text_disabled']};
    }}
    
    /* Labels */
    QLabel {{
        color: {COLORS['text_primary']};
    }}
    QLabel#titleLabel {{
        font-size: 24px;
        font-weight: 700;
        color: {COLORS['text_primary']};
    }}
    QLabel#subtitleLabel {{
        color: {COLORS['text_secondary']};
        font-size: 13px;
        font-weight: 500;
    }}
    
    /* Scroll Areas */
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    QScrollBar:vertical {{
        background-color: transparent;
        width: 10px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {COLORS['border_light']};
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['text_disabled']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* Dropdowns (Combo Box) */
    QComboBox {{
        background-color: {COLORS['bg_card']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border_light']};
        border-radius: 18px; /* Pill shape */
        padding: 8px 16px;
        font-weight: 500;
    }}
    QComboBox::drop-down {{
        border: none;
        padding-right: 12px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['bg_card']};
        color: {COLORS['text_primary']};
        selection-background-color: {COLORS['bg_panel']};
        selection-color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border_light']};
        border-radius: 8px;
    }}
    
    /* Status Bar */
    QStatusBar {{
        background-color: {COLORS['bg_app']};
        color: {COLORS['text_secondary']};
    }}
    """