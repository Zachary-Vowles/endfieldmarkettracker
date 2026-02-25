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

# Product dictionary mapping names to their specific regions
PRODUCT_REGIONS = {
    # Wuling Region
    "Wuling Frozen Pears": Region.WULING,
    "Wuxia Movies": Region.WULING,
    "Nymphsprout": Region.WULING,
    "Eureka Anti-smog Tincture": Region.WULING,
    "Wuling Frozen Pears [pkg]": Region.WULING,
    "Wuxia Movies [pkg]": Region.WULING,
    "Nymphsprout [pkg]": Region.WULING,
    "Eureka Anti-smog Tincture [pkg]": Region.WULING,
    
    # Valley IV Region
    "Ankhorilling Kitchenware": Region.VALLEY,
    "Musbeast Scrimshaw Dangles": Region.VALLEY,
    "Witchcraft Mining Drill": Region.VALLEY,
    "Aggeloi War Tins": Region.VALLEY,
    "Valley Hydroculture Fillets": Region.VALLEY,
    "Unity Syrup": Region.VALLEY,
    "Originium Saplings": Region.VALLEY,
    "Seš'qamam Knucklebones": Region.VALLEY,
    "Astarron Crystals": Region.VALLEY,
    "Vigilant Pickaxes": Region.VALLEY,
    "Hard Noggin Helmets": Region.VALLEY,
    "Scrap Toy Blocks": Region.VALLEY,
    "Ankhorilling Kitchenware [pkg]": Region.VALLEY,
    "Musbeast Scrimshaw Dangles [pkg]": Region.VALLEY,
    "Witchcraft Mining Drill [pkg]": Region.VALLEY,
    "Aggeloi War Tins [pkg]": Region.VALLEY,
    "Valley Hydroculture Fillets [pkg]": Region.VALLEY,
    "Unity Syrup [pkg]": Region.VALLEY,
    "Originium Saplings [pkg]": Region.VALLEY,
    "Seš'qamam Knucklebones [pkg]": Region.VALLEY,
    "Astarron Crystals [pkg]": Region.VALLEY,
    "Vigilant Pickaxes [pkg]": Region.VALLEY,
    "Hard Noggin Helmets [pkg]": Region.VALLEY,
    "Scrap Toy Blocks [pkg]": Region.VALLEY,
}

# Keep this for backward compatibility with regex compiler
KNOWN_PRODUCTS = list(PRODUCT_REGIONS.keys())

# Database
DB_NAME = "prices.db"