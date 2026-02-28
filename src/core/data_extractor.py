"""
Extracts and validates OCR data using Fuzzy Matching for product names.
"""
import difflib
from dataclasses import dataclass
from typing import Optional, Dict, Any
from src.utils.constants import KNOWN_PRODUCTS, PRODUCT_REGIONS

@dataclass
class ProductData:
    name: str = ""  # Default to empty string instead of None to fix Test crashes
    region: Optional[str] = None
    local_price: Optional[int] = None
    friend_price: Optional[int] = None
    average_cost: Optional[int] = None
    quantity_owned: int = 0

class DataExtractor:
    def __init__(self):
        self.known_products = KNOWN_PRODUCTS

    def process_ocr_results(self, raw_results: Dict[str, Any]) -> ProductData:
        """Converts raw OCR dict into structured, validated ProductData"""
        data = ProductData()
        
        # Extract numbers safely, defaulting to None if OCR failed
        data.local_price = self._safe_int(raw_results.get('local_price'))
        data.friend_price = self._safe_int(raw_results.get('friend_price'))
        data.average_cost = self._safe_int(raw_results.get('average_cost'))
        data.quantity_owned = self._safe_int(raw_results.get('quantity_owned'), default=0)

        # Fuzzy Name Matching (Solves OCR typos and prevents crashes)
        raw_name = raw_results.get('product_name')
        if raw_name and isinstance(raw_name, str):
            clean_name = raw_name.strip()
            if clean_name:
                # REJECT if name is just a number (OCR picked up price instead of name)
                if clean_name.isdigit():
                    data.name = ""  # Clear it so it won't match as valid
                    return data  # Return early - this is not a valid product screen
                
                # Try exact match first
                if clean_name in self.known_products:
                    data.name = clean_name
                    matches = [clean_name]
                else:
                    # 0.6 cutoff is stricter - requires closer match
                    matches = difflib.get_close_matches(clean_name, self.known_products, n=1, cutoff=0.6)
                
                if matches:
                    matched_name = matches[0]
                    # Additional safety: check if the match is actually similar
                    similarity = difflib.SequenceMatcher(None, clean_name.lower(), matched_name.lower()).ratio()
                    
                    if similarity >= 0.5:  # Must be at least 50% similar
                        data.name = matched_name
                        region_enum = PRODUCT_REGIONS.get(data.name)
                        data.region = region_enum.value if region_enum else None
                    else:
                        data.name = clean_name  # Keep original if match is too weak
                else:
                    data.name = clean_name  # fallback so it isn't completely empty

        return data

    def _safe_int(self, value: Any, default: Optional[int] = None) -> Optional[int]:
        """Safely parses integers from OCR output."""
        if value is None:
            return default
        if isinstance(value, str):
            if not value.strip():  # Empty string
                return default
            cleaned = ''.join(c for c in value if c.isdigit())
            return int(cleaned) if cleaned else default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def is_valid_reading(self, data: ProductData) -> bool:
        """
        Allows partial data! It just needs enough info for the current capture state.
        """
        # Validate price ranges to reject OCR errors
        if data.local_price is not None:
            if data.local_price < 10 or data.local_price > 9500:
                data.local_price = None  # Reject impossible price
        
        if data.friend_price is not None:
            if data.friend_price < 10 or data.friend_price > 9000:
                data.friend_price = None  # Reject impossible price
        # State 1 Check: We have a known Name AND a Local Price
        is_main_screen = bool(data.name in self.known_products and data.local_price and data.local_price > 0)
        
        # State 2 Check: We have a Friend Price that looks reasonable (not OCR noise)
        # Note: We don't require name validation here because the friend price screen
        # might not show the product name clearly, or OCR might fail on it
        is_friend_screen = bool(data.friend_price and data.friend_price > 100 and data.friend_price < 10000)
        
        return is_main_screen or is_friend_screen