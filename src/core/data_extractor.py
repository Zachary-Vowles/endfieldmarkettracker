"""
Data extractor - processes OCR results into structured data
"""

import re
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from src.utils.constants import KNOWN_PRODUCTS, Region
from loguru import logger

@dataclass
class ProductData:
    """Structured product data from game"""
    name: str
    region: str
    local_price: int
    friend_price: Optional[int] = None
    average_cost: Optional[int] = None
    quantity_owned: int = 0
    vs_local_percent: Optional[float] = None
    vs_owned_percent: Optional[float] = None
    reading_id: Optional[int] = None

class DataExtractor:
    """Extracts structured data from OCR text"""
    
    def __init__(self):
        """Initialize the extractor"""
        self.product_patterns = self._compile_product_patterns()
    
    def _compile_product_patterns(self) -> Dict:
        """Compile regex patterns for known products"""
        patterns = {}
        for product in KNOWN_PRODUCTS:
            # Create fuzzy matching pattern
            escaped = re.escape(product.lower())
            patterns[product] = re.compile(escaped, re.IGNORECASE)
        return patterns
    
    def extract_product_name(self, text: str) -> Optional[str]:
        """Extract product name from OCR text"""
        text_lower = str(text).lower()
        
        # Check against known products
        for product, pattern in self.product_patterns.items():
            if pattern.search(text_lower):
                return product # Return the exact, properly formatted name
        
        # If no match, return the text cleaned up - can replace with return None to be stricter, maybe will cause an issue - check known product list.
        cleaned = text.strip().replace("[pkg]", "").strip()
        return cleaned if cleaned else None
    
    def extract_price(self, text) -> Optional[int]:
        """Extract price value from text or int safely"""
        # If it's already a number from the OCR engine, just return it!
        if isinstance(text, int):
            return text
            
        if not text:
            return None
            
        # Remove currency symbols and non-digit characters
        cleaned = re.sub(r'[^\d]', '', str(text))
        
        try:
            return int(cleaned) if cleaned else None
        except ValueError:
            return None
    
    def extract_percentage(self, text: str) -> Optional[float]:
        """Extract percentage value from text"""
        if not text:
            return None
        
        # Match patterns like +40.5%, -15.2%, 80.9%
        match = re.search(r'([+-]?\\d+\\.?\\d*)%', text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None
    
    def extract_quantity(self, text: str) -> int:
        """Extract quantity owned from text"""
        if not text:
            return 0
        
        # Look for "Owned: X" or just a number
        match = re.search(r'Owned[\s]*(\d+)', str(text), re.IGNORECASE) ##old version was: match = re.search(r'Owned[:\\s]*(\\d+)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Try to find any number
        numbers = re.findall(r'\d+', str(text)) ##old version was: numbers = re.findall(r'\\d+', text)
        if numbers:
            return int(numbers[0])
        
        return 0
    
    def determine_region(self, name: str) -> str:
        """Determine region strictly from the verified product name"""
        from src.utils.constants import PRODUCT_REGIONS
        if name in PRODUCT_REGIONS:
            return PRODUCT_REGIONS[name].value
        return Region.WULING.value


    def process_ocr_results(self, ocr_results: Dict) -> Optional[ProductData]:
        """Process raw OCR results into structured product data"""
        logger.debug(f"Raw OCR Dictionary: {ocr_results}")
        try:
            # Safely grab strings
            name_text = str(ocr_results.get('product_name', ''))
            name = self.extract_product_name(name_text)
            
            local_price = self.extract_price(ocr_results.get('local_price'))
            friend_price = self.extract_price(ocr_results.get('friend_price'))
            
            # To stitch screens, we need AT LEAST a product name OR a friend price. 
            # If we have neither, the screen is useless to us right now.
            if not name and not friend_price:
                return None

            product_data = ProductData(
                name=name if name else "",
                region=self.determine_region(name) if name else "",
                local_price=local_price if local_price else 0,
                friend_price=friend_price,
                average_cost=self.extract_price(ocr_results.get('average_cost')),
                quantity_owned=self.extract_quantity(ocr_results.get('quantity_owned', '')),
                vs_local_percent=self.extract_percentage(str(ocr_results.get('vs_local', ''))),
                vs_owned_percent=self.extract_percentage(str(ocr_results.get('vs_owned', '')))
            )

            logger.info(f"Created ProductData: {product_data}")
            return product_data
            
        except Exception as e:
            logger.error(f"Error processing OCR results: {e}")
            return None
    def calculate_profit_potential(self, data: ProductData) -> Optional[int]:
        """Calculate absolute profit potential"""
        if data.friend_price and data.local_price:
            return data.friend_price - data.local_price
        return None
    
    def is_valid_reading(self, data: ProductData) -> bool:
        """Validate that the reading makes sense"""
        # Basic sanity checks
        if not data.name or len(data.name) < 3:
            return False
        
        if data.local_price and (data.local_price < 0 or data.local_price > 1000000):
            return False
        
        if data.friend_price and (data.friend_price < 0 or data.friend_price > 1000000):
            return False
        
        return True