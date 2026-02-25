"""
Constants for Endfield Market Tracker
"""

from enum import Enum

class Region(Enum):
    WULING = "wuling"
    VALLEY = "valley"

# Currency symbols matching the game
CURRENCIES = {
    Region.WULING: "HZ",
    Region.VALLEY: "◆"  # Yellow diamond-like symbol used in Valley
}

# UI Colors matching Endfield aesthetic (Updated from Mockup)
COLORS = {
    # Backgrounds
    'bg_app': '#1a1a1a',           # Deep dark outer background
    'bg_panel': '#f5f5f5',         # The clean white/grey main inner panel
    'bg_card': '#ffffff',          # Pure white for product cards
    'bg_card_hover': '#f9fafb',
    'bg_header': '#ffffff',
    'bg_dark_log': '#222222',      # Dark background for the screenshot log
    
    # Accents
    'accent_teal': '#00d4aa',      # Wuling/HZ color
    'accent_yellow': '#fceb00',    # The signature Endfield bright yellow
    'accent_yellow_hover': '#e6d600',
    
    # Text
    'text_primary': '#1f2937',     # Dark grey text for light panels
    'text_secondary': '#6b7280',   # Muted grey
    'text_disabled': '#9ca3af',
    'text_inverse': '#ffffff',     # White text for dark areas
    'text_dark_ui': '#e5e7eb',     # Light text for the dark log panel
    
    # Status
    'success': '#22c55e',          # Tailwind green-500
    'danger': '#ef4444',           # Tailwind red-500
    
    # Buttons
    'btn_start_bg': '#ffffff',
    'btn_start_text': '#111827',
    'btn_stop_bg': '#3a3a3a',
    'btn_stop_hover': '#222222',
    'btn_outline_border': '#9ca3af',
    
    # Borders
    'border_light': '#d1d5db',
    'border_dark': '#3a3a3a',
}

# Screen capture settings - OPTIMIZED FOR 2560x1440 FULLSCREEN
CAPTURE_SETTINGS = {
    'fps': 10,  # Frames per second for screen checking
    'resolution': (2560, 1440),  # Target resolution - 1440p
    'confidence_threshold': 0.75,  # Slightly lower for better detection
}

# UI Regions for OCR - CALIBRATED FOR 2560x1440 FULLSCREEN
DEFAULT_ROIS = {
    'product_name':   {'x': 961,  'y': 366, 'w': 705, 'h': 54},
    'local_price':    {'x': 1922, 'y': 1017, 'w': 121, 'h': 64},
    'average_cost':   {'x': 688,  'y': 856, 'w': 150, 'h': 50},
    'quantity_owned': {'x': 210,  'y': 585, 'w': 210, 'h': 50},
    'friend_price':   {'x': 710, 'y': 804, 'w': 132, 'h': 44}
}

# Auto-detection settings
AUTO_DETECT = {
    'enabled': True,
    'check_interval_ms': 100,  # Check every 100ms
    'stability_frames': 3,     # Require 3 stable frames before capture
    'price_change_threshold': 50,  # Minimum price change to trigger new reading
}

# Product names we expect to see (for validation)
KNOWN_PRODUCTS = [
    "Wuling Frozen Pears",
    "Eureka Anti-smog Tincture", 
    "Wuxia Movies",
    "Nymphsprout",
    "Witchcraft Mining Drill",
    "Military Canned Food",
    "Valley Specialty",
    "Industrial Precision Component",
    "Gallic Standard Cookware",
    "Victoria Crown",
    "Lungmen Freshwater",
    "Sami Herbal Mix",
    "Iberian Dried Fish",
    "Kazimierz Knight Figurine",
    "Laterano Sacramental Candle",
    "Higashi Tea Set",
    "Sargon Spice",
    "Ursus Timber",
    "Yanese Silks",
    "Leithanian Instruments",
]

# Database
DB_NAME = "prices.db"