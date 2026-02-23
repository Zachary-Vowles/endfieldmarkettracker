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

# UI Colors matching Endfield aesthetic
COLORS = {
    # Backgrounds
    'bg_primary': '#0d0d0d',
    'bg_secondary': '#1a1a1a', 
    'bg_card': '#252525',
    'bg_card_hover': '#2f2f2f',
    
    # Accents
    'accent_teal': '#00d4aa',      # Wuling/HZ color
    'accent_teal_dark': '#00a884',
    'accent_yellow': '#ffd700',     # Valley color
    'accent_yellow_dark': '#ccac00',
    
    # Text
    'text_primary': '#ffffff',
    'text_secondary': '#a0a0a0',
    'text_disabled': '#666666',
    
    # Status
    'success': '#4caf50',
    'success_dark': '#388e3c',
    'danger': '#f44336',
    'danger_dark': '#d32f2f',
    'warning': '#ff9800',
    
    # Buttons
    'button_start': '#ffffff',
    'button_start_hover': '#f0f0f0',
    'button_stop_start': '#ff6b6b',
    'button_stop_end': '#ee5a5a',
    
    # Borders
    'border_light': '#3a3a3a',
    'border_highlight': '#00d4aa',
}

# Screen capture settings - OPTIMIZED FOR 2560x1440 FULLSCREEN
CAPTURE_SETTINGS = {
    'fps': 10,  # Frames per second for screen checking
    'resolution': (2560, 1440),  # Target resolution - 1440p
    'confidence_threshold': 0.75,  # Slightly lower for better detection
}

# UI Regions for OCR - CALIBRATED FOR 2560x1440 FULLSCREEN
# These are absolute pixel coordinates for 2560x1440
# ROI Coordinates for 2560x1440 Resolution
# These are the 'Golden Standard' coordinates for 2560x1440p. 
# The 'Smart Scaler' will adjust these if you ever change resolution.
DEFAULT_ROIS = {
    'product_name':   {'x': 950,  'y': 285, 'w': 650, 'h': 75},
    'local_price':    {'x': 1950, 'y': 365, 'w': 180, 'h': 55},
    'average_cost':   {'x': 210,  'y': 635, 'w': 210, 'h': 50},
    'quantity_owned': {'x': 210,  'y': 585, 'w': 210, 'h': 50},
    'friend_price':   {'x': 1550, 'y': 440, 'w': 250, 'h': 65}
}

# Auto-detection settings
AUTO_DETECT = {
    'stability_frames': 3,
    'price_change_threshold': 5
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

# Auto-detection settings
AUTO_DETECT = {
    'enabled': True,
    'check_interval_ms': 100,  # Check every 100ms
    'stability_frames': 3,     # Require 3 stable frames before capture
    'price_change_threshold': 50,  # Minimum price change to trigger new reading
}